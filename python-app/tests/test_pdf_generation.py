"""
Test for PDF generation service to reproduce and verify fix for Style 'Title' already defined error
"""

import pytest
from datetime import date, datetime
from app.services.pdf import PDFGenerationService
from app.models.form import AccommodationFormData, TenantDetails, BankDetails, AddressHistoryEntry, Contacts, MedicalDetails, Employment, PassportDetails, CurrentLivingArrangement, LandlordContact, OtherDetails, OccupationAgreement, ConsentAndDeclaration, Declaration


def create_minimal_form_data():
    """Create minimal valid form data for testing"""
    
    # Create minimal tenant details
    tenant = TenantDetails(
        full_name="John Doe",
        date_of_birth=date(1990, 1, 1),
        place_of_birth="London, UK",
        email="john.doe@example.com",
        telephone="07123456789",
        employers_name="Test Company Ltd",
        gender="male",
        ni_number="AB123456C",
        car=False,
        bicycle=False,
        right_to_live_in_uk=True,
        room_occupancy="just_you",
        other_names_has=False,
        medical_condition_has=False
    )
    
    # Create minimal bank details
    bank = BankDetails(
        bank_name="Test Bank",
        postcode="SW1A 1AA",
        account_no="12345678",
        sort_code="12-34-56"
    )
    
    # Create minimal address history
    address_history = [
        AddressHistoryEntry(
            address="123 Test Street, London, SW1A 1AA",
            from_date=date(2023, 1, 1),
            to_date=None,
            landlord_name="Test Landlord",
            landlord_tel="07987654321",
            landlord_email="landlord@example.com"
        )
    ]
    
    # Create minimal contacts
    contacts = Contacts(
        next_of_kin="Jane Doe",
        relationship="Sister",
        address="456 Test Road, London, SW1A 1BB",
        contact_number="07111222333"
    )
    
    # Create minimal medical details
    medical = MedicalDetails(
        gp_practice="Test GP Practice",
        doctor_name="Dr. Test",
        doctor_address="789 Medical Street, London, SW1A 1CC",
        doctor_telephone="02012345678"
    )
    
    # Create minimal employment
    employment = Employment(
        employer_name_address="Test Company Ltd, 100 Business Street, London, SW1A 1DD",
        job_title="Software Developer",
        manager_name="Test Manager",
        manager_tel="02087654321",
        manager_email="manager@testcompany.com",
        date_of_employment=date(2022, 1, 1),
        present_salary=50000.0
    )
    
    # Create minimal passport details
    passport = PassportDetails(
        passport_number="123456789",
        date_of_issue=date(2020, 1, 1),
        place_of_issue="London"
    )
    
    # Create minimal landlord contact
    landlord_contact = LandlordContact(
        name="Current Landlord",
        address="Current Address, London, SW1A 1EE",
        tel="02011111111",
        email="current@landlord.com"
    )
    
    # Create minimal current living arrangement
    current_living = CurrentLivingArrangement(
        landlord_knows=True,
        notice_end_date=date(2024, 12, 31),
        reason_leaving="Moving closer to work",
        landlord_reference=True,
        landlord_contact=landlord_contact
    )
    
    # Create minimal other details
    other = OtherDetails(
        pets_has=False,
        pets_details=None,
        smoke=False,
        coliving_has=False,
        coliving_details=None
    )
    
    # Create minimal occupation agreement
    occupation = OccupationAgreement(
        single_occupancy_agree=True,
        hmo_terms_agree=True,
        no_unlisted_occupants=True,
        no_smoking=True,
        kitchen_cooking_only=True
    )
    
    # Create minimal declaration
    declaration = Declaration(
        main_home=True,
        enquiries_permission=True,
        certify_no_judgements=True,
        certify_no_housing_debt=True,
        certify_no_landlord_debt=True,
        certify_no_abuse=True
    )
    
    # Create minimal consent and declaration
    consent = ConsentAndDeclaration(
        consent_given=True,
        signature="John Doe",
        date=date(2024, 8, 8),
        print_name="John Doe",
        declaration=declaration,
        declaration_signature="John Doe",
        declaration_date=date(2024, 8, 8),
        declaration_print_name="John Doe"
    )
    
    # Create the complete form data
    form_data = AccommodationFormData(
        tenant_details=tenant,
        bank_details=bank,
        address_history=address_history,
        contacts=contacts,
        medical_details=medical,
        employment=employment,
        passport_details=passport,
        current_living_arrangement=current_living,
        other_details=other,
        occupation_agreement=occupation,
        consent_and_declaration=consent,
        form_submitted_at=datetime.utcnow(),
        client_ip="127.0.0.1"
    )
    
    return form_data


def test_pdf_generation_service_initialization():
    """Test that PDFGenerationService can be initialized without errors"""
    # This should now work after fixing the duplicate 'Title' style issue
    service = PDFGenerationService()
    assert service is not None
    assert service.styles is not None
    assert 'CustomTitle' in service.styles.byName
    print("PDF service initialized successfully")


@pytest.mark.asyncio
async def test_pdf_generation_end_to_end():
    """Test full PDF generation process"""
    # Create the service
    service = PDFGenerationService()
    
    # Create test form data
    form_data = create_minimal_form_data()
    
    # Generate filename
    filename = await service.generate_filename(form_data)
    assert filename.endswith('.pdf')
    assert 'John' in filename
    assert 'Doe' in filename
    
    # Generate PDF
    pdf_buffer = await service.generate_pdf(form_data)
    assert pdf_buffer is not None
    
    # Check that buffer has content
    pdf_content = pdf_buffer.read()
    assert len(pdf_content) > 0
    
    # Reset buffer position for future use
    pdf_buffer.seek(0)
    
    print(f"Successfully generated PDF with {len(pdf_content)} bytes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])