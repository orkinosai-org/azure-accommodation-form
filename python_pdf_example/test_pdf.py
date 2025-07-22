#!/usr/bin/env python3
"""
Test script for the Python PDF generation example.

This script demonstrates both ReportLab and FPDF backends
for generating PDFs from Azure Accommodation Form data.
"""

import os
import sys
import json
from pdf_generator import AccommodationFormPDFGenerator

def test_pdf_generation():
    """Test PDF generation with sample data."""
    print("Testing Python PDF Generation for Azure Accommodation Form")
    print("=" * 60)
    
    # Sample form data matching the C# FormData structure
    sample_data = {
        "TenantDetails": {
            "FullName": "Alice Johnson",
            "DateOfBirth": "1985-03-15",
            "Email": "alice.johnson@example.com", 
            "Telephone": "+44207123456",
            "PlaceOfBirth": "Manchester",
            "EmployersName": "Digital Solutions Ltd",
            "Gender": "Female",
            "NiNumber": "CD987654A",
            "Car": False,
            "Bicycle": True,
            "RightToLiveInUk": True,
            "RoomOccupancy": "Single"
        },
        "BankDetails": {
            "BankName": "HSBC Bank plc",
            "Postcode": "EC2V 6DN",
            "AccountNo": "87654321",
            "SortCode": "40-02-02"
        },
        "AddressHistory": [
            {
                "Address": "45 Victoria Street, London SW1H 0EU",
                "From": "2021-06-01",
                "To": "2024-01-15",
                "LandlordName": "Property Management Co",
                "LandlordTel": "+44207555666",
                "LandlordEmail": "contact@propertymanagement.co.uk"
            },
            {
                "Address": "12 High Street, Manchester M1 1AA",
                "From": "2018-09-01", 
                "To": "2021-05-31",
                "LandlordName": "Private Landlord",
                "LandlordTel": "+44161777888",
                "LandlordEmail": "landlord@email.com"
            }
        ],
        "Contacts": {
            "NextOfKin": "Robert Johnson",
            "Relationship": "Father",
            "Address": "78 Oak Avenue, Manchester M20 2BB",
            "ContactNumber": "+44161999000"
        },
        "MedicalDetails": {
            "GpPractice": "City Medical Centre",
            "DoctorName": "Dr. Sarah Williams",
            "DoctorAddress": "123 Health Street, London W1A 1AA",
            "DoctorTelephone": "+44207444555"
        },
        "Employment": {
            "EmployerName": "Digital Solutions Ltd",
            "EmployerAddress": "50 Tech Plaza, London EC1A 1BB",
            "JobTitle": "Senior Software Engineer",
            "ManagerName": "James Smith",
            "ManagerTel": "+44207333444",
            "ManagerEmail": "j.smith@digitalsolutions.com",
            "DateOfEmployment": "2020-03-01",
            "PresentSalary": "£65,000"
        },
        "EmploymentChange": "No changes expected in the foreseeable future",
        "PassportDetails": {
            "PassportNumber": "123456789",
            "DateOfIssue": "2019-05-20",
            "PlaceOfIssue": "London"
        },
        "CurrentLivingArrangement": {
            "LandlordKnows": True,
            "NoticeEndDate": "2024-03-31",
            "ReasonLeaving": "Seeking larger accommodation",
            "LandlordReference": True,
            "LandlordContact": {
                "Name": "Property Management Co",
                "Tel": "+44207555666",
                "Address": "101 Management Road, London SW1A 1AA",
                "Email": "contact@propertymanagement.co.uk"
            }
        },
        "Other": {
            "Pets": {"HasPets": False, "Details": ""},
            "Smoke": False,
            "Coliving": {"HasColiving": False, "Details": ""}
        },
        "OccupationAgreement": {
            "SingleOccupancyAgree": True,
            "HmoTermsAgree": True,
            "NoUnlistedOccupants": True,
            "NoSmoking": True,
            "KitchenCookingOnly": True
        },
        "ConsentAndDeclaration": {
            "ConsentGiven": True,
            "Signature": "Alice Johnson",
            "Date": "2024-01-15",
            "PrintName": "Alice Johnson",
            "Declaration": {
                "MainHome": True,
                "EnquiriesPermission": True,
                "CertifyNoJudgements": True,
                "CertifyNoHousingDebt": True,
                "CertifyNoLandlordDebt": True,
                "CertifyNoAbuse": True
            },
            "DeclarationSignature": "Alice Johnson",
            "DeclarationDate": "2024-01-15",
            "DeclarationPrintName": "Alice Johnson"
        }
    }
    
    # Create output directory
    output_dir = "/tmp/python_pdf_test"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test ReportLab backend
    try:
        print("Testing ReportLab backend...")
        generator = AccommodationFormPDFGenerator(backend="reportlab")
        filename = generator.generate_filename(sample_data)
        output_path = os.path.join(output_dir, f"reportlab_{filename}")
        
        result = generator.generate_pdf_from_json(sample_data, output_path, "TEST-12345")
        
        if os.path.exists(result) and os.path.getsize(result) > 0:
            print(f"✅ ReportLab PDF generated successfully: {result}")
            print(f"   File size: {os.path.getsize(result)} bytes")
        else:
            print("❌ ReportLab PDF generation failed")
            
    except ImportError as e:
        print(f"⚠️  ReportLab not available: {e}")
        print("   Install with: pip install reportlab")
    except Exception as e:
        print(f"❌ ReportLab error: {e}")
    
    # Test FPDF backend
    try:
        print("\nTesting FPDF backend...")
        generator = AccommodationFormPDFGenerator(backend="fpdf")
        filename = generator.generate_filename(sample_data)
        output_path = os.path.join(output_dir, f"fpdf_{filename}")
        
        result = generator.generate_pdf_from_json(sample_data, output_path, "TEST-12345")
        
        if os.path.exists(result) and os.path.getsize(result) > 0:
            print(f"✅ FPDF PDF generated successfully: {result}")
            print(f"   File size: {os.path.getsize(result)} bytes")
        else:
            print("❌ FPDF PDF generation failed")
            
    except ImportError as e:
        print(f"⚠️  FPDF not available: {e}")
        print("   Install with: pip install fpdf2")
    except Exception as e:
        print(f"❌ FPDF error: {e}")
    
    print(f"\nTest completed. Output files in: {output_dir}")
    print("\nTo install dependencies:")
    print("   pip install -r requirements.txt")


if __name__ == "__main__":
    test_pdf_generation()