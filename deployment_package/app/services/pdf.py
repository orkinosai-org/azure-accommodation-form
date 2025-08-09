"""
PDF generation service using ReportLab
"""

import io
import logging
from datetime import datetime
from typing import BinaryIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas

from app.models.form import AccommodationFormData
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class PDFGenerationService:
    """Service for generating PDF documents from form data"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom PDF styles"""
        # Custom Title style (renamed to avoid conflict with existing 'Title' style)
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#007acc'),
            alignment=1  # Center alignment
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#333333'),
            backColor=colors.HexColor('#f0f0f0'),
            leftIndent=5,
            rightIndent=5
        ))
        
        # Field label style
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=2
        ))
        
        # Field value style
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8
        ))
    
    async def generate_filename(self, form_data: AccommodationFormData) -> str:
        """Generate PDF filename according to specification"""
        tenant = form_data.tenant_details
        
        # Clean name (remove special characters)
        first_name = ''.join(c for c in tenant.full_name.split()[0] if c.isalnum())
        last_name = ''.join(c for c in tenant.full_name.split()[-1] if c.isalnum())
        
        # Format timestamp
        timestamp = datetime.utcnow().strftime("%d%m%Y%H%M")
        
        filename = f"{first_name}_{last_name}_Application_Form_{timestamp}.pdf"
        return filename
    
    async def generate_pdf(self, form_data: AccommodationFormData) -> BinaryIO:
        """Generate PDF document from form data"""
        buffer = io.BytesIO()
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=1*inch
            )
            
            # Build content
            story = []
            
            # Add title
            story.append(Paragraph("Accommodation Application Form", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Add metadata
            metadata_table = Table([
                ['Application ID:', await self.generate_filename(form_data)],
                ['Submitted:', form_data.form_submitted_at.strftime("%Y-%m-%d %H:%M:%S UTC") if form_data.form_submitted_at else "N/A"],
                ['Client IP:', form_data.client_ip or "N/A"]
            ], colWidths=[2*inch, 4*inch])
            
            metadata_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metadata_table)
            story.append(Spacer(1, 20))
            
            # Add sections
            story.extend(await self._add_tenant_details(form_data.tenant_details))
            story.extend(await self._add_bank_details(form_data.bank_details))
            story.extend(await self._add_address_history(form_data.address_history))
            story.extend(await self._add_contacts(form_data.contacts))
            story.extend(await self._add_medical_details(form_data.medical_details))
            story.extend(await self._add_employment(form_data.employment))
            story.extend(await self._add_passport_details(form_data.passport_details))
            story.extend(await self._add_current_living_arrangement(form_data.current_living_arrangement))
            story.extend(await self._add_other_details(form_data.other_details))
            story.extend(await self._add_occupation_agreement(form_data.occupation_agreement))
            story.extend(await self._add_consent_declaration(form_data.consent_and_declaration))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info(f"PDF generated successfully for {form_data.tenant_details.full_name}")
            return buffer
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    async def _add_tenant_details(self, tenant):
        """Add tenant details section"""
        story = []
        story.append(Paragraph("1. Tenant Details", self.styles['SectionHeader']))
        
        data = [
            ['Full Name:', tenant.full_name],
            ['Date of Birth:', str(tenant.date_of_birth)],
            ['Place of Birth:', tenant.place_of_birth],
            ['Email:', tenant.email],
            ['Telephone:', tenant.telephone],
            ['Employer:', tenant.employers_name],
            ['Gender:', tenant.gender.value],
            ['NI Number:', tenant.ni_number],
            ['Has Car:', 'Yes' if tenant.car else 'No'],
            ['Has Bicycle:', 'Yes' if tenant.bicycle else 'No'],
            ['Right to Live in UK:', 'Yes' if tenant.right_to_live_in_uk else 'No'],
            ['Room Occupancy:', tenant.room_occupancy.value.replace('_', ' ').title()],
        ]
        
        if tenant.other_names_has:
            data.append(['Other Names:', tenant.other_names_details or 'N/A'])
        
        if tenant.medical_condition_has:
            data.append(['Medical Condition:', tenant.medical_condition_details or 'N/A'])
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_bank_details(self, bank):
        """Add bank details section"""
        story = []
        story.append(Paragraph("2. Bank Details", self.styles['SectionHeader']))
        
        data = [
            ['Bank Name:', bank.bank_name],
            ['Postcode:', bank.postcode],
            ['Account Number:', bank.account_no],
            ['Sort Code:', bank.sort_code],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_address_history(self, addresses):
        """Add address history section"""
        story = []
        story.append(Paragraph("3. Address History (3 Years)", self.styles['SectionHeader']))
        
        for i, addr in enumerate(addresses, 1):
            story.append(Paragraph(f"Address {i}:", self.styles['FieldLabel']))
            
            data = [
                ['Address:', addr.address],
                ['From Date:', str(addr.from_date)],
                ['To Date:', str(addr.to_date) if addr.to_date else 'Current'],
                ['Landlord Name:', addr.landlord_name],
                ['Landlord Tel:', addr.landlord_tel],
                ['Landlord Email:', addr.landlord_email],
            ]
            
            table = Table(data, colWidths=[2.5*inch, 3.5*inch])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1, 10))
        
        return story
    
    async def _add_contacts(self, contacts):
        """Add contacts section"""
        story = []
        story.append(Paragraph("4. Emergency Contact", self.styles['SectionHeader']))
        
        data = [
            ['Next of Kin:', contacts.next_of_kin],
            ['Relationship:', contacts.relationship],
            ['Address:', contacts.address],
            ['Contact Number:', contacts.contact_number],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_medical_details(self, medical):
        """Add medical details section"""
        story = []
        story.append(Paragraph("5. Medical Details", self.styles['SectionHeader']))
        
        data = [
            ['GP Practice:', medical.gp_practice],
            ['Doctor Name:', medical.doctor_name],
            ['Doctor Address:', medical.doctor_address],
            ['Doctor Telephone:', medical.doctor_telephone],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_employment(self, employment):
        """Add employment section"""
        story = []
        story.append(Paragraph("6. Current Employment", self.styles['SectionHeader']))
        
        data = [
            ['Employer Name & Address:', employment.employer_name_address],
            ['Job Title:', employment.job_title],
            ['Manager Name:', employment.manager_name],
            ['Manager Tel:', employment.manager_tel],
            ['Manager Email:', employment.manager_email],
            ['Date of Employment:', str(employment.date_of_employment)],
            ['Present Salary:', f"£{employment.present_salary:,.2f}"],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_passport_details(self, passport):
        """Add passport details section"""
        story = []
        story.append(Paragraph("7. Passport Details", self.styles['SectionHeader']))
        
        data = [
            ['Passport Number:', passport.passport_number],
            ['Date of Issue:', str(passport.date_of_issue)],
            ['Place of Issue:', passport.place_of_issue],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_current_living_arrangement(self, living):
        """Add current living arrangement section"""
        story = []
        story.append(Paragraph("8. Current Living Arrangement", self.styles['SectionHeader']))
        
        data = [
            ['Landlord Knows:', 'Yes' if living.landlord_knows else 'No'],
            ['Notice End Date:', str(living.notice_end_date) if living.notice_end_date else 'N/A'],
            ['Reason for Leaving:', living.reason_leaving],
            ['Landlord Reference:', 'Yes' if living.landlord_reference else 'No'],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 10))
        
        # Landlord contact details
        story.append(Paragraph("Current Landlord Contact:", self.styles['FieldLabel']))
        contact_data = [
            ['Name:', living.landlord_contact.name],
            ['Address:', living.landlord_contact.address],
            ['Telephone:', living.landlord_contact.tel],
            ['Email:', living.landlord_contact.email],
        ]
        
        contact_table = Table(contact_data, colWidths=[2.5*inch, 3.5*inch])
        contact_table.setStyle(self._get_table_style())
        story.append(contact_table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_other_details(self, other):
        """Add other details section"""
        story = []
        story.append(Paragraph("9. Other Details", self.styles['SectionHeader']))
        
        data = [
            ['Has Pets:', 'Yes' if other.pets_has else 'No'],
            ['Smoker:', 'Yes' if other.smoke else 'No'],
            ['Has Coliving Experience:', 'Yes' if other.coliving_has else 'No'],
        ]
        
        if other.pets_has and other.pets_details:
            data.append(['Pet Details:', other.pets_details])
        
        if other.coliving_has and other.coliving_details:
            data.append(['Coliving Details:', other.coliving_details])
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_occupation_agreement(self, agreement):
        """Add occupation agreement section"""
        story = []
        story.append(Paragraph("10. Occupation Agreement", self.styles['SectionHeader']))
        
        data = [
            ['Single Occupancy Agreement:', 'Yes' if agreement.single_occupancy_agree else 'No'],
            ['HMO Terms Agreement:', 'Yes' if agreement.hmo_terms_agree else 'No'],
            ['No Unlisted Occupants:', 'Yes' if agreement.no_unlisted_occupants else 'No'],
            ['No Smoking Agreement:', 'Yes' if agreement.no_smoking else 'No'],
            ['Kitchen Cooking Only:', 'Yes' if agreement.kitchen_cooking_only else 'No'],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 15))
        
        return story
    
    async def _add_consent_declaration(self, consent):
        """Add consent and declaration section"""
        story = []
        story.append(Paragraph("11. Consent & Declaration", self.styles['SectionHeader']))
        
        # Consent section
        story.append(Paragraph("Consent:", self.styles['FieldLabel']))
        consent_data = [
            ['Consent Given:', 'Yes' if consent.consent_given else 'No'],
            ['Signature:', consent.signature],
            ['Date:', str(consent.date)],
            ['Print Name:', consent.print_name],
        ]
        
        consent_table = Table(consent_data, colWidths=[2.5*inch, 3.5*inch])
        consent_table.setStyle(self._get_table_style())
        story.append(consent_table)
        story.append(Spacer(1, 10))
        
        # Declaration section
        story.append(Paragraph("Declaration:", self.styles['FieldLabel']))
        decl = consent.declaration
        declaration_data = [
            ['Main Home Declaration:', 'Yes' if decl.main_home else 'No'],
            ['Enquiries Permission:', 'Yes' if decl.enquiries_permission else 'No'],
            ['No CCJs/Judgements:', 'Yes' if decl.certify_no_judgements else 'No'],
            ['No Housing Debt:', 'Yes' if decl.certify_no_housing_debt else 'No'],
            ['No Landlord Debt:', 'Yes' if decl.certify_no_landlord_debt else 'No'],
            ['No Property Abuse:', 'Yes' if decl.certify_no_abuse else 'No'],
            ['Declaration Signature:', consent.declaration_signature],
            ['Declaration Date:', str(consent.declaration_date)],
            ['Declaration Print Name:', consent.declaration_print_name],
        ]
        
        declaration_table = Table(declaration_data, colWidths=[2.5*inch, 3.5*inch])
        declaration_table.setStyle(self._get_table_style())
        story.append(declaration_table)
        story.append(Spacer(1, 15))
        
        return story
    
    def _get_table_style(self):
        """Get standard table style"""
        return TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ])