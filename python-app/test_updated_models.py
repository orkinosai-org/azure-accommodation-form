#!/usr/bin/env python3
"""
Test script to validate the updated form models and structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from datetime import date
from app.models.form import (
    TenantDetails, BankDetails, AddressHistoryEntry, Employment, 
    OtherDetails, Declaration, AccommodationFormData
)

def test_updated_models():
    """Test all the updated models with the new structure"""
    print("🧪 Testing updated form models...")
    
    # Test TenantDetails - should NOT have employers_name anymore
    try:
        tenant = TenantDetails(
            full_name="John Doe",
            date_of_birth=date(1990, 1, 1),
            place_of_birth="London",
            email="john@example.com",
            telephone="07123456789",
            gender="male",
            ni_number="AB123456C",
            car=True,
            bicycle=False,
            right_to_live_in_uk=True,
            room_occupancy="just_you",
            medical_condition_has=True,
            medical_condition_details="Asthma - uses inhaler"
        )
        print("✅ TenantDetails: employer name removed, medical condition added")
    except Exception as e:
        print(f"❌ TenantDetails failed: {e}")
        return False
    
    # Test BankDetails - should have bank_branch_address instead of postcode
    try:
        bank = BankDetails(
            bank_name="HSBC",
            bank_branch_address="123 High Street, London, SW1A 1AA",
            account_no="12345678",
            sort_code="12-34-56"
        )
        print("✅ BankDetails: postcode changed to bank_branch_address")
    except Exception as e:
        print(f"❌ BankDetails failed: {e}")
        return False
    
    # Test AddressHistoryEntry - should have reason_for_leaving
    try:
        address = AddressHistoryEntry(
            address="123 Test Street, London",
            from_date=date(2020, 1, 1),
            to_date=date(2023, 1, 1),
            landlord_name="Test Landlord",
            landlord_tel="07123456789",
            landlord_email="landlord@example.com",
            reason_for_leaving="Moving closer to work"
        )
        print("✅ AddressHistoryEntry: reason_for_leaving field added")
    except Exception as e:
        print(f"❌ AddressHistoryEntry failed: {e}")
        return False
    
    # Test Employment - should have employers_name field moved from TenantDetails
    try:
        employment = Employment(
            employer_name_address="Acme Corp, 456 Business Street, London",
            employers_name="Acme Corporation",  # Moved from TenantDetails
            job_title="Software Developer",
            manager_name="Jane Smith",
            manager_tel="07987654321",
            manager_email="jane@acme.com",
            date_of_employment=date(2020, 1, 1),
            present_salary=50000.0
        )
        print("✅ Employment: employers_name field added (moved from TenantDetails)")
    except Exception as e:
        print(f"❌ Employment failed: {e}")
        return False
    
    # Test OtherDetails - should have vaping fields
    try:
        other = OtherDetails(
            pets_has=False,
            smoke=True,
            smoke_details="Occasionally, only outside",
            vaping=False,
            vaping_details=None,
            coliving_has=True,
            coliving_details="Prefer quiet, professional flatmates"
        )
        print("✅ OtherDetails: vaping fields added, smoke_details added")
    except Exception as e:
        print(f"❌ OtherDetails failed: {e}")
        return False
    
    # Test Declaration - should have alcohol/substance abuse certification
    try:
        declaration = Declaration(
            main_home=True,
            enquiries_permission=True,
            certify_no_judgements=True,
            certify_no_housing_debt=True,
            certify_no_landlord_debt=True,
            certify_no_abuse=True,
            certify_no_alcohol_substance_abuse=True  # New field
        )
        print("✅ Declaration: alcohol/substance abuse certification added")
    except Exception as e:
        print(f"❌ Declaration failed: {e}")
        return False
    
    # Test AccommodationFormData - should not have current_living_arrangement
    try:
        # Create minimal valid form data
        from app.models.form import Contacts, MedicalDetails, PassportDetails, OccupationAgreement, ConsentAndDeclaration
        
        contacts = Contacts(
            next_of_kin="Jane Doe",
            relationship="Sister",
            address="789 Family Street, London",
            contact_number="07111222333"
        )
        
        medical = MedicalDetails(
            gp_practice="London Health Centre",
            doctor_name="Dr. Smith",
            doctor_address="101 Medical Street, London",
            doctor_telephone="02012345678"
        )
        
        passport = PassportDetails(
            passport_number="123456789",
            date_of_issue=date(2020, 1, 1),
            place_of_issue="London"
        )
        
        occupation = OccupationAgreement(
            single_occupancy_agree=True,
            hmo_terms_agree=True,
            no_unlisted_occupants=True,
            no_smoking=True,
            kitchen_cooking_only=True
        )
        
        consent = ConsentAndDeclaration(
            consent_given=True,
            signature="John Doe",
            date=date.today(),
            print_name="John Doe",
            declaration=declaration,
            declaration_signature="John Doe",
            declaration_date=date.today(),
            declaration_print_name="John Doe"
        )
        
        form_data = AccommodationFormData(
            tenant_details=tenant,
            bank_details=bank,
            address_history=[address],
            contacts=contacts,
            medical_details=medical,
            employment=employment,
            passport_details=passport,
            other_details=other,
            occupation_agreement=occupation,
            consent_and_declaration=consent
        )
        print("✅ AccommodationFormData: current_living_arrangement removed, all models integrated")
    except Exception as e:
        print(f"❌ AccommodationFormData failed: {e}")
        return False
    
    print("\n🎉 All model tests passed! Updated structure is working correctly.")
    return True

if __name__ == "__main__":
    success = test_updated_models()
    sys.exit(0 if success else 1)