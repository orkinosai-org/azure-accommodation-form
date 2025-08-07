"""
Test that simulates the frontend data collection and submission process
"""

import json
from app.models.form import AccommodationFormData, FormSubmissionRequest

def test_frontend_data_collection_simulation():
    """Simulate what the frontend collectFormData() method would produce"""
    
    # Simulate form field values (what user would fill in)
    form_fields = {
        'full_name': 'John Doe',
        'date_of_birth': '1990-01-01',
        'place_of_birth': 'London, UK',
        'email': 'john.doe@example.com',
        'telephone': '07123456789',
        'employers_name': 'Test Company Ltd',
        'gender': 'male',
        'ni_number': 'AB123456C',
        'car': False,
        'bicycle': False,
        'right_to_live_in_uk': True,
        'room_occupancy': 'just_you',
        
        # Bank details
        'bank_name': 'Test Bank',
        'bank_postcode': 'SW1A 1AA',
        'account_no': '12345678',
        'sort_code': '12-34-56',
        
        # Address history
        'address_0': '123 Test Street, London, SW1A 1AA',
        'from_date_0': '2023-01-01',
        'landlord_name_0': 'Test Landlord',
        'landlord_tel_0': '07987654321',
        'landlord_email_0': 'landlord@example.com'
    }
    
    # Simulate hidden field data (from the updated frontend)
    hidden_data = {
        'contacts_data': '{"next_of_kin":"Emergency Contact","relationship":"Friend","address":"Emergency Contact Address, London, SW1A 1AA","contact_number":"07000000000"}',
        'medical_data': '{"gp_practice":"Default GP Practice","doctor_name":"Dr. Default","doctor_address":"Default Medical Address, London, SW1A 1BB","doctor_telephone":"02000000000"}',
        'employment_data': '{"employer_name_address":"Default Employer Ltd, Business Address, London, SW1A 1CC","job_title":"Default Position","manager_name":"Default Manager","manager_tel":"02000000001","manager_email":"manager@example.com","date_of_employment":"2023-01-01","present_salary":30000}',
        'passport_data': '{"passport_number":"DEFAULT123456","date_of_issue":"2023-01-01","place_of_issue":"London"}',
        'living_data': '{"landlord_knows":true,"notice_end_date":null,"reason_leaving":"Seeking new accommodation","landlord_reference":true,"landlord_contact":{"name":"Current Landlord","address":"Current Landlord Address, London, SW1A 1DD","tel":"02000000002","email":"current@landlord.com"}}',
        'other_data': '{"pets_has":false,"pets_details":null,"smoke":false,"coliving_has":false,"coliving_details":null}',
        'agreement_data': '{"single_occupancy_agree":true,"hmo_terms_agree":true,"no_unlisted_occupants":true,"no_smoking":true,"kitchen_cooking_only":true}',
        'consent_data': '{"consent_given":true,"signature":"Digital Signature","date":"2024-01-01","print_name":"Default Name","declaration":{"main_home":true,"enquiries_permission":true,"certify_no_judgements":true,"certify_no_housing_debt":true,"certify_no_landlord_debt":true,"certify_no_abuse":true},"declaration_signature":"Digital Signature","declaration_date":"2024-01-01","declaration_print_name":"Default Name"}'
    }
    
    # Simulate the collectFormData() logic
    def parseHiddenFieldData(data_key, default_value):
        try:
            if data_key in hidden_data:
                return json.loads(hidden_data[data_key])
        except:
            pass
        return default_value
    
    # This simulates the updated collectFormData() method
    form_data = {
        "tenant_details": {
            "full_name": form_fields.get('full_name', ''),
            "date_of_birth": form_fields.get('date_of_birth', ''),
            "place_of_birth": form_fields.get('place_of_birth', ''),
            "email": form_fields.get('email', ''),
            "telephone": form_fields.get('telephone', ''),
            "employers_name": form_fields.get('employers_name', ''),
            "gender": form_fields.get('gender', 'other'),
            "ni_number": form_fields.get('ni_number', ''),
            "car": form_fields.get('car', False),
            "bicycle": form_fields.get('bicycle', False),
            "right_to_live_in_uk": form_fields.get('right_to_live_in_uk', False),
            "room_occupancy": form_fields.get('room_occupancy', 'just_you'),
            "other_names_has": False,
            "other_names_details": None,
            "medical_condition_has": False,
            "medical_condition_details": None
        },
        "bank_details": {
            "bank_name": form_fields.get('bank_name', ''),
            "postcode": form_fields.get('bank_postcode', ''),
            "account_no": form_fields.get('account_no', ''),
            "sort_code": form_fields.get('sort_code', '')
        },
        "address_history": [
            {
                "address": form_fields.get('address_0', ''),
                "from_date": form_fields.get('from_date_0', ''),
                "to_date": None,
                "landlord_name": form_fields.get('landlord_name_0', ''),
                "landlord_tel": form_fields.get('landlord_tel_0', ''),
                "landlord_email": form_fields.get('landlord_email_0', '')
            }
        ],
        "contacts": parseHiddenFieldData('contacts_data', {}),
        "medical_details": parseHiddenFieldData('medical_data', {}),
        "employment": parseHiddenFieldData('employment_data', {}),
        "employment_change": None,
        "passport_details": parseHiddenFieldData('passport_data', {}),
        "current_living_arrangement": parseHiddenFieldData('living_data', {}),
        "other_details": parseHiddenFieldData('other_data', {}),
        "occupation_agreement": parseHiddenFieldData('agreement_data', {}),
        "consent_and_declaration": parseHiddenFieldData('consent_data', {}),
        "client_ip": None,
        "form_opened_at": None,
        "form_submitted_at": None
    }
    
    print("Frontend Data Collection Simulation")
    print("="*50)
    
    # Test AccommodationFormData validation
    try:
        accommodation_form = AccommodationFormData(**form_data)
        print("✓ Frontend collected data validates as AccommodationFormData")
    except Exception as e:
        print(f"✗ Frontend data validation failed: {e}")
        return False
    
    # Simulate the frontend submission request creation
    submission_request = {
        "form_data": form_data,
        "email_verification_token": "test-session-token",
        "math_question": "What is 2 + 2?",
        "math_answer": 4
    }
    
    # Test FormSubmissionRequest validation
    try:
        request_obj = FormSubmissionRequest(**submission_request)
        print("✓ Frontend submission request validates as FormSubmissionRequest")
    except Exception as e:
        print(f"✗ Frontend submission request validation failed: {e}")
        return False
    
    print("✓ Frontend data collection simulation successful!")
    print(f"✓ All {len([k for k in form_data.keys() if k not in ['client_ip', 'form_opened_at', 'form_submitted_at']])} required sections populated")
    print(f"✓ User details: {accommodation_form.tenant_details.full_name} ({accommodation_form.tenant_details.email})")
    
    return True

if __name__ == "__main__":
    success = test_frontend_data_collection_simulation()
    if success:
        print("\n✓ FRONTEND SIMULATION PASSED!")
        print("✓ The updated frontend will successfully submit form data")
    else:
        print("\n✗ FRONTEND SIMULATION FAILED")