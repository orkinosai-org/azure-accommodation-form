"""
Pydantic models for form data validation
"""

from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class RoomOccupancyEnum(str, Enum):
    JUST_YOU = "just_you"
    YOU_AND_SOMEONE_ELSE = "you_and_someone_else"

class TenantDetails(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    place_of_birth: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telephone: str = Field(..., min_length=10, max_length=20)
    employers_name: str = Field(..., min_length=2, max_length=100)
    gender: GenderEnum
    ni_number: str = Field(..., min_length=9, max_length=13)  # UK National Insurance number
    car: bool = False
    bicycle: bool = False
    right_to_live_in_uk: bool
    room_occupancy: RoomOccupancyEnum
    
    # Optional fields
    other_names_has: bool = False
    other_names_details: Optional[str] = None
    medical_condition_has: bool = False
    medical_condition_details: Optional[str] = None
    
    @validator('ni_number')
    def validate_ni_number(cls, v):
        # Basic UK NI number validation
        import re
        pattern = r'^[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z][0-9]{6}[A-D]$'
        if not re.match(pattern, v.upper().replace(' ', '')):
            raise ValueError('Invalid UK National Insurance number format')
        return v.upper().replace(' ', '')

class BankDetails(BaseModel):
    bank_name: str = Field(..., min_length=2, max_length=100)
    postcode: str = Field(..., min_length=5, max_length=10)
    account_no: str = Field(..., min_length=8, max_length=8)
    sort_code: str = Field(..., min_length=6, max_length=8)
    
    @validator('account_no')
    def validate_account_number(cls, v):
        # UK bank account number should be 8 digits
        if not v.isdigit() or len(v) != 8:
            raise ValueError('Account number must be 8 digits')
        return v
    
    @validator('sort_code')
    def validate_sort_code(cls, v):
        # UK sort code format: 12-34-56 or 123456
        sort_code = v.replace('-', '').replace(' ', '')
        if not sort_code.isdigit() or len(sort_code) != 6:
            raise ValueError('Sort code must be 6 digits')
        return f"{sort_code[:2]}-{sort_code[2:4]}-{sort_code[4:6]}"

class AddressHistoryEntry(BaseModel):
    address: str = Field(..., min_length=10, max_length=200)
    from_date: date
    to_date: Optional[date] = None  # None means current address
    landlord_name: str = Field(..., min_length=2, max_length=100)
    landlord_tel: str = Field(..., min_length=10, max_length=20)
    landlord_email: EmailStr

class Contacts(BaseModel):
    next_of_kin: str = Field(..., min_length=2, max_length=100)
    relationship: str = Field(..., min_length=2, max_length=50)
    address: str = Field(..., min_length=10, max_length=200)
    contact_number: str = Field(..., min_length=10, max_length=20)

class MedicalDetails(BaseModel):
    gp_practice: str = Field(..., min_length=2, max_length=100)
    doctor_name: str = Field(..., min_length=2, max_length=100)
    doctor_address: str = Field(..., min_length=10, max_length=200)
    doctor_telephone: str = Field(..., min_length=10, max_length=20)

class Employment(BaseModel):
    employer_name_address: str = Field(..., min_length=10, max_length=200)
    job_title: str = Field(..., min_length=2, max_length=100)
    manager_name: str = Field(..., min_length=2, max_length=100)
    manager_tel: str = Field(..., min_length=10, max_length=20)
    manager_email: EmailStr
    date_of_employment: date
    present_salary: float = Field(..., gt=0)

class PassportDetails(BaseModel):
    passport_number: str = Field(..., min_length=6, max_length=15)
    date_of_issue: date
    place_of_issue: str = Field(..., min_length=2, max_length=100)

class LandlordContact(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=10, max_length=200)
    tel: str = Field(..., min_length=10, max_length=20)
    email: EmailStr

class CurrentLivingArrangement(BaseModel):
    landlord_knows: bool
    notice_end_date: Optional[date] = None
    reason_leaving: str = Field(..., min_length=10, max_length=500)
    landlord_reference: bool
    landlord_contact: LandlordContact

class OtherDetails(BaseModel):
    pets_has: bool = False
    pets_details: Optional[str] = None
    smoke: bool = False
    coliving_has: bool = False
    coliving_details: Optional[str] = None

class OccupationAgreement(BaseModel):
    single_occupancy_agree: bool
    hmo_terms_agree: bool
    no_unlisted_occupants: bool
    no_smoking: bool
    kitchen_cooking_only: bool

class Declaration(BaseModel):
    main_home: bool
    enquiries_permission: bool
    certify_no_judgements: bool
    certify_no_housing_debt: bool
    certify_no_landlord_debt: bool
    certify_no_abuse: bool

class ConsentAndDeclaration(BaseModel):
    consent_given: bool
    signature: str = Field(..., min_length=1)  # Base64 encoded signature or typed name
    date: date
    print_name: str = Field(..., min_length=2, max_length=100)
    declaration: Declaration
    declaration_signature: str = Field(..., min_length=1)
    declaration_date: date
    declaration_print_name: str = Field(..., min_length=2, max_length=100)

class AccommodationFormData(BaseModel):
    """Complete accommodation form data model"""
    tenant_details: TenantDetails
    bank_details: BankDetails
    address_history: List[AddressHistoryEntry] = Field(..., min_items=1, max_items=10)
    contacts: Contacts
    medical_details: MedicalDetails
    employment: Employment
    employment_change: Optional[str] = None
    passport_details: PassportDetails
    current_living_arrangement: CurrentLivingArrangement
    other_details: OtherDetails
    occupation_agreement: OccupationAgreement
    consent_and_declaration: ConsentAndDeclaration
    
    # Metadata
    client_ip: Optional[str] = None
    form_opened_at: Optional[datetime] = None
    form_submitted_at: Optional[datetime] = None

class FormSubmissionRequest(BaseModel):
    """Form submission request model"""
    form_data: AccommodationFormData
    email_verification_token: str
    captcha_token: str

class FormSubmissionResponse(BaseModel):
    """Form submission response model"""
    submission_id: str
    status: Literal["success", "error"]
    message: str
    pdf_filename: Optional[str] = None
    timestamp: datetime

# MFA and email verification models
class EmailVerificationRequest(BaseModel):
    email: EmailStr
    email_confirm: EmailStr
    captcha_token: str

class EmailVerificationResponse(BaseModel):
    verification_id: str
    message: str
    expires_at: datetime

class MFATokenRequest(BaseModel):
    verification_id: str
    token: str

class MFATokenResponse(BaseModel):
    verified: bool
    message: str
    session_token: Optional[str] = None