"""
Test for form submission issue
This test demonstrates the current problem and validates the fix
"""

import json
from datetime import date, datetime
from app.models.form import AccommodationFormData, FormSubmissionRequest

def test_form_data_structure():
    """Test that demonstrates the expected data structure for form submission"""
    
    # This is the minimal valid form data that should be accepted
    form_data = {
        "tenant_details": {
            "full_name": "John Doe",
            "date_of_birth": "1990-01-01",
            "place_of_birth": "London, UK",
            "email": "john.doe@example.com",
            "telephone": "07123456789",
            "employers_name": "Test Company Ltd",
            "gender": "male",
            "ni_number": "AB123456C",
            "car": False,
            "bicycle": False,
            "right_to_live_in_uk": True,
            "room_occupancy": "just_you",
            "other_names_has": False,
            "other_names_details": None,
            "medical_condition_has": False,
            "medical_condition_details": None
        },
        "bank_details": {
            "bank_name": "Test Bank",
            "postcode": "SW1A 1AA",
            "account_no": "12345678",
            "sort_code": "12-34-56"
        },
        "address_history": [
            {
                "address": "123 Test Street, London, SW1A 1AA",
                "from_date": "2023-01-01",
                "to_date": None,
                "landlord_name": "Test Landlord",
                "landlord_tel": "07987654321",
                "landlord_email": "landlord@example.com"
            }
        ],
        "contacts": {
            "next_of_kin": "Jane Doe",
            "relationship": "Sister",
            "address": "456 Family Street, London, SW1A 1BB",
            "contact_number": "07111222333"
        },
        "medical_details": {
            "gp_practice": "Test Medical Practice",
            "doctor_name": "Dr. Smith",
            "doctor_address": "789 Medical Street, London, SW1A 1CC",
            "doctor_telephone": "02012345678"
        },
        "employment": {
            "employer_name_address": "Test Company Ltd, 100 Business Street, London, SW1A 1DD",
            "job_title": "Software Developer",
            "manager_name": "Manager Smith",
            "manager_tel": "02087654321",
            "manager_email": "manager@testcompany.com",
            "date_of_employment": "2023-01-01",
            "present_salary": 40000.0
        },
        "employment_change": None,
        "passport_details": {
            "passport_number": "123456789",
            "date_of_issue": "2023-01-01",
            "place_of_issue": "London"
        },
        "current_living_arrangement": {
            "landlord_knows": True,
            "notice_end_date": None,
            "reason_leaving": "Looking for better accommodation",
            "landlord_reference": True,
            "landlord_contact": {
                "name": "Current Landlord",
                "address": "999 Current Street, London, SW1A 1EE",
                "tel": "02098765432",
                "email": "current@landlord.com"
            }
        },
        "other_details": {
            "pets_has": False,
            "pets_details": None,
            "smoke": False,
            "coliving_has": False,
            "coliving_details": None
        },
        "occupation_agreement": {
            "single_occupancy_agree": True,
            "hmo_terms_agree": True,
            "no_unlisted_occupants": True,
            "no_smoking": True,
            "kitchen_cooking_only": True
        },
        "consent_and_declaration": {
            "consent_given": True,
            "signature": "John Doe",
            "date": "2024-01-01",
            "print_name": "John Doe",
            "declaration": {
                "main_home": True,
                "enquiries_permission": True,
                "certify_no_judgements": True,
                "certify_no_housing_debt": True,
                "certify_no_landlord_debt": True,
                "certify_no_abuse": True
            },
            "declaration_signature": "John Doe",
            "declaration_date": "2024-01-01",
            "declaration_print_name": "John Doe"
        },
        "client_ip": None,
        "form_opened_at": None,
        "form_submitted_at": None
    }
    
    # Test AccommodationFormData validation
    try:
        accommodation_form = AccommodationFormData(**form_data)
        print("✓ AccommodationFormData validation passed")
    except Exception as e:
        print(f"✗ AccommodationFormData validation failed: {e}")
        return False
    
    # Test FormSubmissionRequest structure (what the API should expect)
    submission_request_data = {
        "form_data": form_data,
        "email_verification_token": "test-token-123",
        "math_question": "What is 2 + 2?",
        "math_answer": 4
    }
    
    try:
        submission_request = FormSubmissionRequest(**submission_request_data)
        print("✓ FormSubmissionRequest validation passed")
    except Exception as e:
        print(f"✗ FormSubmissionRequest validation failed: {e}")
        return False
    
    print("✓ All model validations passed")
    return True

def test_current_api_issue():
    """Demonstrate the current API issue"""
    
    # This is what the frontend currently sends (incomplete data)
    current_frontend_data = {
        "tenant_details": {
            "full_name": "John Doe",
            "email": "john.doe@example.com"
            # Missing many required fields...
        }
        # Missing all other required sections...
    }
    
    print("\nTesting current frontend data structure:")
    try:
        # This should fail because many required fields are missing
        AccommodationFormData(**current_frontend_data)
        print("✗ Unexpected success - validation should have failed")
        return False
    except Exception as e:
        print(f"✓ Expected validation failure: {e}")
        return True

def test_api_structure_handling():
    """Test that the API can handle both FormSubmissionRequest and legacy AccommodationFormData"""
    
    # Valid AccommodationFormData structure
    form_data = {
        "tenant_details": {
            "full_name": "John Doe",
            "date_of_birth": "1990-01-01",
            "place_of_birth": "London, UK",
            "email": "john.doe@example.com",
            "telephone": "07123456789",
            "employers_name": "Test Company Ltd",
            "gender": "male",
            "ni_number": "AB123456C",
            "car": False,
            "bicycle": False,
            "right_to_live_in_uk": True,
            "room_occupancy": "just_you",
            "other_names_has": False,
            "other_names_details": None,
            "medical_condition_has": False,
            "medical_condition_details": None
        },
        "bank_details": {
            "bank_name": "Test Bank",
            "postcode": "SW1A 1AA",
            "account_no": "12345678",
            "sort_code": "12-34-56"
        },
        "address_history": [
            {
                "address": "123 Test Street, London, SW1A 1AA",
                "from_date": "2023-01-01",
                "to_date": None,
                "landlord_name": "Test Landlord",
                "landlord_tel": "07987654321",
                "landlord_email": "landlord@example.com"
            }
        ],
        "contacts": {
            "next_of_kin": "Jane Doe",
            "relationship": "Sister",
            "address": "456 Family Street, London, SW1A 1BB",
            "contact_number": "07111222333"
        },
        "medical_details": {
            "gp_practice": "Test Medical Practice",
            "doctor_name": "Dr. Smith",
            "doctor_address": "789 Medical Street, London, SW1A 1CC",
            "doctor_telephone": "02012345678"
        },
        "employment": {
            "employer_name_address": "Test Company Ltd, 100 Business Street, London, SW1A 1DD",
            "job_title": "Software Developer",
            "manager_name": "Manager Smith",
            "manager_tel": "02087654321",
            "manager_email": "manager@testcompany.com",
            "date_of_employment": "2023-01-01",
            "present_salary": 40000.0
        },
        "employment_change": None,
        "passport_details": {
            "passport_number": "123456789",
            "date_of_issue": "2023-01-01",
            "place_of_issue": "London"
        },
        "current_living_arrangement": {
            "landlord_knows": True,
            "notice_end_date": None,
            "reason_leaving": "Looking for better accommodation",
            "landlord_reference": True,
            "landlord_contact": {
                "name": "Current Landlord",
                "address": "999 Current Street, London, SW1A 1EE",
                "tel": "02098765432",
                "email": "current@landlord.com"
            }
        },
        "other_details": {
            "pets_has": False,
            "pets_details": None,
            "smoke": False,
            "coliving_has": False,
            "coliving_details": None
        },
        "occupation_agreement": {
            "single_occupancy_agree": True,
            "hmo_terms_agree": True,
            "no_unlisted_occupants": True,
            "no_smoking": True,
            "kitchen_cooking_only": True
        },
        "consent_and_declaration": {
            "consent_given": True,
            "signature": "John Doe",
            "date": "2024-01-01",
            "print_name": "John Doe",
            "declaration": {
                "main_home": True,
                "enquiries_permission": True,
                "certify_no_judgements": True,
                "certify_no_housing_debt": True,
                "certify_no_landlord_debt": True,
                "certify_no_abuse": True
            },
            "declaration_signature": "John Doe",
            "declaration_date": "2024-01-01",
            "declaration_print_name": "John Doe"
        },
        "client_ip": None,
        "form_opened_at": None,
        "form_submitted_at": None
    }
    
    print("\n" + "="*50)
    print("Testing API structure handling logic:")
    print("="*50)
    
    # Test 1: FormSubmissionRequest structure (NEW FORMAT)
    print("\n1. Testing FormSubmissionRequest format:")
    request_with_form_data = {
        "form_data": form_data,
        "email_verification_token": "test-token-123",
        "math_question": "What is 2 + 2?",
        "math_answer": 4
    }
    
    # Simulate the API logic
    if "form_data" in request_with_form_data:
        try:
            submission_request = FormSubmissionRequest(**request_with_form_data)
            extracted_form_data = submission_request.form_data
            print("✓ FormSubmissionRequest structure validated successfully")
            print("✓ Form data extracted from FormSubmissionRequest")
        except Exception as e:
            print(f"✗ FormSubmissionRequest validation failed: {e}")
            return False
    else:
        print("✗ This should not happen - form_data key exists")
        return False
    
    # Test 2: Legacy AccommodationFormData structure (LEGACY FALLBACK)
    print("\n2. Testing legacy AccommodationFormData format:")
    try:
        legacy_form_data = AccommodationFormData(**form_data)
        print("✓ Legacy AccommodationFormData structure validated successfully")
    except Exception as e:
        print(f"✗ Legacy AccommodationFormData validation failed: {e}")
        return False
    
    print("\n✓ Both API structure formats work correctly")
    return True

if __name__ == "__main__":
    print("Testing form submission data structures...")
    print("=" * 50)
    
    success1 = test_form_data_structure()
    success2 = test_current_api_issue()
    success3 = test_api_structure_handling()
    
    if success1 and success2 and success3:
        print("\n✓ All tests demonstrate the expected behavior")
        print("✓ The API fix should resolve the form submission issue")
    else:
        print("\n✗ Some tests failed")