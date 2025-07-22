"""
Python PDF Generation Example for Azure Accommodation Form

This module provides an alternative implementation of PDF generation 
using Python libraries (ReportLab and FPDF), demonstrating how the 
form data could be processed with Python instead of the existing C# solution.

Note: This is a reference implementation. The production application 
uses the C# PdfGenerationService which is fully integrated and working.
"""

import json
import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# ReportLab implementation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# FPDF implementation
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class AccommodationFormPDFGenerator:
    """
    PDF generator for Azure Accommodation Form using Python libraries.
    
    Supports both ReportLab (more advanced) and FPDF (simpler) backends.
    """
    
    def __init__(self, backend: str = "reportlab"):
        """
        Initialize PDF generator with specified backend.
        
        Args:
            backend: Either "reportlab" or "fpdf"
        """
        self.backend = backend
        if backend == "reportlab" and not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab not available. Install with: pip install reportlab")
        elif backend == "fpdf" and not FPDF_AVAILABLE:
            raise ImportError("FPDF not available. Install with: pip install fpdf2")
    
    def generate_pdf_from_json(self, form_data: Dict[str, Any], output_path: str, 
                              submission_id: Optional[str] = None) -> str:
        """
        Generate PDF from form data dictionary.
        
        Args:
            form_data: Dictionary containing form data matching the C# FormData model
            output_path: Path where PDF should be saved
            submission_id: Optional submission ID to include in PDF
            
        Returns:
            Path to generated PDF file
        """
        if self.backend == "reportlab":
            return self._generate_with_reportlab(form_data, output_path, submission_id)
        else:
            return self._generate_with_fpdf(form_data, output_path, submission_id)
    
    def _generate_with_reportlab(self, form_data: Dict[str, Any], output_path: str, 
                                submission_id: Optional[str] = None) -> str:
        """Generate PDF using ReportLab (advanced features)."""
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        story = []
        
        # Title
        story.append(Paragraph("Azure Accommodation Application Form", title_style))
        
        if submission_id:
            story.append(Paragraph(f"Submission ID: {submission_id}", styles['Normal']))
        
        story.append(Paragraph(f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", 
                             styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add sections
        self._add_section_reportlab(story, "1. Tenant Details", form_data.get('TenantDetails', {}), styles)
        self._add_section_reportlab(story, "2. Bank Details", form_data.get('BankDetails', {}), styles)
        self._add_address_history_reportlab(story, form_data.get('AddressHistory', []), styles)
        self._add_section_reportlab(story, "4. Contacts", form_data.get('Contacts', {}), styles)
        self._add_section_reportlab(story, "5. Medical Details", form_data.get('MedicalDetails', {}), styles)
        self._add_section_reportlab(story, "6. Employment", form_data.get('Employment', {}), styles)
        self._add_section_reportlab(story, "7. Employment Change", 
                                   {'EmploymentChange': form_data.get('EmploymentChange', '')}, styles)
        self._add_section_reportlab(story, "8. Passport Details", form_data.get('PassportDetails', {}), styles)
        self._add_section_reportlab(story, "9. Current Living Arrangement", 
                                   form_data.get('CurrentLivingArrangement', {}), styles)
        self._add_section_reportlab(story, "10. Other Details", form_data.get('Other', {}), styles)
        self._add_section_reportlab(story, "11. Occupation Agreement", 
                                   form_data.get('OccupationAgreement', {}), styles)
        self._add_section_reportlab(story, "12. Consent & Declaration", 
                                   form_data.get('ConsentAndDeclaration', {}), styles)
        
        doc.build(story)
        return output_path
    
    def _add_section_reportlab(self, story, title: str, section_data: Dict[str, Any], styles):
        """Add a section to the ReportLab document."""
        story.append(Paragraph(title, styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for key, value in section_data.items():
            if value and not isinstance(value, dict):
                story.append(Paragraph(f"<b>{self._format_field_name(key)}:</b> {value}", styles['Normal']))
        
        story.append(Spacer(1, 15))
    
    def _add_address_history_reportlab(self, story, addresses, styles):
        """Add address history section to ReportLab document."""
        story.append(Paragraph("3. Address History", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for i, address in enumerate(addresses):
            story.append(Paragraph(f"<b>Address {i+1}:</b>", styles['Normal']))
            for key, value in address.items():
                if value:
                    story.append(Paragraph(f"  {self._format_field_name(key)}: {value}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 15))
    
    def _generate_with_fpdf(self, form_data: Dict[str, Any], output_path: str, 
                           submission_id: Optional[str] = None) -> str:
        """Generate PDF using FPDF (simpler implementation)."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'Azure Accommodation Application Form', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 10)
        if submission_id:
            pdf.cell(0, 10, f'Submission ID: {submission_id}', 0, 1)
        
        pdf.cell(0, 10, f'Generated: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC', 0, 1)
        pdf.ln(10)
        
        # Add sections
        self._add_section_fpdf(pdf, "1. Tenant Details", form_data.get('TenantDetails', {}))
        self._add_section_fpdf(pdf, "2. Bank Details", form_data.get('BankDetails', {}))
        self._add_address_history_fpdf(pdf, form_data.get('AddressHistory', []))
        self._add_section_fpdf(pdf, "4. Contacts", form_data.get('Contacts', {}))
        self._add_section_fpdf(pdf, "5. Medical Details", form_data.get('MedicalDetails', {}))
        self._add_section_fpdf(pdf, "6. Employment", form_data.get('Employment', {}))
        self._add_section_fpdf(pdf, "7. Employment Change", 
                              {'EmploymentChange': form_data.get('EmploymentChange', '')})
        self._add_section_fpdf(pdf, "8. Passport Details", form_data.get('PassportDetails', {}))
        self._add_section_fpdf(pdf, "9. Current Living Arrangement", 
                              form_data.get('CurrentLivingArrangement', {}))
        self._add_section_fpdf(pdf, "10. Other Details", form_data.get('Other', {}))
        self._add_section_fpdf(pdf, "11. Occupation Agreement", 
                              form_data.get('OccupationAgreement', {}))
        self._add_section_fpdf(pdf, "12. Consent & Declaration", 
                              form_data.get('ConsentAndDeclaration', {}))
        
        pdf.output(output_path)
        return output_path
    
    def _add_section_fpdf(self, pdf: FPDF, title: str, section_data: Dict[str, Any]):
        """Add a section to the FPDF document."""
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, title, 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for key, value in section_data.items():
            if value and not isinstance(value, dict):
                pdf.cell(0, 6, f'{self._format_field_name(key)}: {value}', 0, 1)
        
        pdf.ln(5)
    
    def _add_address_history_fpdf(self, pdf: FPDF, addresses):
        """Add address history section to FPDF document."""
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '3. Address History', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for i, address in enumerate(addresses):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f'Address {i+1}:', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            for key, value in address.items():
                if value:
                    pdf.cell(0, 6, f'  {self._format_field_name(key)}: {value}', 0, 1)
            pdf.ln(2)
        
        pdf.ln(5)
    
    def _format_field_name(self, field_name: str) -> str:
        """Convert camelCase field names to readable format."""
        # Simple conversion from camelCase to Title Case
        result = ""
        for i, char in enumerate(field_name):
            if i == 0:
                result += char.upper()
            elif char.isupper():
                result += f" {char}"
            else:
                result += char
        return result
    
    def generate_filename(self, form_data: Dict[str, Any], submission_time: Optional[datetime.datetime] = None) -> str:
        """
        Generate filename matching the C# implementation format.
        
        Format: FirstName_LastName_Application_Form_DDMMYYYYHHMM.pdf
        """
        tenant_details = form_data.get('TenantDetails', {})
        full_name = tenant_details.get('FullName', 'Unknown_User')
        
        # Split name and sanitize
        name_parts = full_name.split()
        first_name = self._sanitize_filename(name_parts[0] if name_parts else 'Unknown')
        last_name = self._sanitize_filename(name_parts[-1] if len(name_parts) > 1 else 'User')
        
        if submission_time is None:
            submission_time = datetime.datetime.utcnow()
        
        timestamp = submission_time.strftime("%d%m%Y%H%M")
        
        return f"{first_name}_{last_name}_Application_Form_{timestamp}.pdf"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove invalid filename characters."""
        invalid_chars = '<>:"/\\|?*'
        sanitized = ''.join(c for c in filename if c not in invalid_chars and c != ' ')
        return sanitized if sanitized else 'Unknown'


def example_usage():
    """Demonstrate how to use the PDF generator."""
    # Sample form data (matching C# FormData structure)
    sample_data = {
        "TenantDetails": {
            "FullName": "John Doe",
            "DateOfBirth": "1990-01-01",
            "Email": "john.doe@example.com",
            "Telephone": "+44123456789",
            "PlaceOfBirth": "London",
            "EmployersName": "Tech Corp",
            "Gender": "Male",
            "NiNumber": "AB123456C",
            "Car": True,
            "Bicycle": False,
            "RightToLiveInUk": True,
            "RoomOccupancy": "Single"
        },
        "BankDetails": {
            "BankName": "Example Bank",
            "Postcode": "SW1A 1AA",
            "AccountNo": "12345678",
            "SortCode": "12-34-56"
        },
        "AddressHistory": [
            {
                "Address": "123 Example Street, London",
                "From": "2020-01-01",
                "To": "2023-12-31",
                "LandlordName": "Jane Smith",
                "LandlordTel": "+44987654321",
                "LandlordEmail": "jane@example.com"
            }
        ],
        "Contacts": {
            "NextOfKin": "Mary Doe",
            "Relationship": "Sister",
            "Address": "456 Family Road, London",
            "ContactNumber": "+44111222333"
        },
        "Employment": {
            "EmployerName": "Tech Corp Ltd",
            "JobTitle": "Software Developer",
            "PresentSalary": "£50,000"
        },
        "ConsentAndDeclaration": {
            "ConsentGiven": True,
            "Signature": "John Doe",
            "PrintName": "John Doe"
        }
    }
    
    # Generate PDF with ReportLab
    if REPORTLAB_AVAILABLE:
        generator = AccommodationFormPDFGenerator(backend="reportlab")
        filename = generator.generate_filename(sample_data)
        output_path = f"/tmp/{filename}"
        generator.generate_pdf_from_json(sample_data, output_path, "12345")
        print(f"ReportLab PDF generated: {output_path}")
    
    # Generate PDF with FPDF
    if FPDF_AVAILABLE:
        generator = AccommodationFormPDFGenerator(backend="fpdf")
        filename = generator.generate_filename(sample_data)
        output_path = f"/tmp/fpdf_{filename}"
        generator.generate_pdf_from_json(sample_data, output_path, "12345")
        print(f"FPDF PDF generated: {output_path}")


if __name__ == "__main__":
    example_usage()