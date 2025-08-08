using System.ComponentModel.DataAnnotations;
using BlazorApp.Validation;

namespace BlazorApp.Models;

public class TenantDetails
{
    [Required(ErrorMessage = "Full Name is required.")]
    [StringLength(100, MinimumLength = 2, ErrorMessage = "Full Name must be between 2 and 100 characters.")]
    [Display(Name = "Full Name")]
    public string FullName { get; set; } = string.Empty;

    [Required(ErrorMessage = "Date of Birth is required.")]
    [Display(Name = "Date of Birth")]
    [DataType(DataType.Date)]
    public DateTime? DateOfBirth { get; set; }

    [StringLength(100, ErrorMessage = "Place of Birth cannot exceed 100 characters.")]
    [Display(Name = "Place of Birth")]
    public string PlaceOfBirth { get; set; } = string.Empty;

    [Required(ErrorMessage = "Email is required.")]
    [EmailAddress(ErrorMessage = "Please enter a valid email address.")]
    [StringLength(254, ErrorMessage = "Email cannot exceed 254 characters.")]
    [Display(Name = "Email")]
    public string Email { get; set; } = string.Empty;

    [Required(ErrorMessage = "Telephone is required.")]
    [Phone(ErrorMessage = "Please enter a valid phone number.")]
    [StringLength(20, MinimumLength = 10, ErrorMessage = "Telephone must be between 10 and 20 characters.")]
    [Display(Name = "Telephone")]
    public string Telephone { get; set; } = string.Empty;

    [StringLength(100, ErrorMessage = "Employer's Name cannot exceed 100 characters.")]
    [Display(Name = "Employer's Name")]
    public string EmployersName { get; set; } = string.Empty;

    [Display(Name = "Gender")]
    public Gender? Gender { get; set; }

    [StringLength(13, MinimumLength = 9, ErrorMessage = "NI Number must be between 9 and 13 characters.")]
    [Display(Name = "NI Number")]
    public string NiNumber { get; set; } = string.Empty;

    [Display(Name = "Do you have a car?")]
    public bool Car { get; set; }

    [Display(Name = "Do you have a bicycle?")]
    public bool Bicycle { get; set; }

    [Display(Name = "Do you have the right to live in the UK?")]
    public bool RightToLiveInUk { get; set; }

    public OtherNames OtherNames { get; set; } = new();

    [Display(Name = "Room Occupancy")]
    public RoomOccupancy? RoomOccupancy { get; set; }

    public MedicalCondition MedicalCondition { get; set; } = new();
}

public class BankDetails
{
    [StringLength(100, ErrorMessage = "Bank Name cannot exceed 100 characters.")]
    [Display(Name = "Name of Bank")]
    public string BankName { get; set; } = string.Empty;

    [StringLength(10, MinimumLength = 5, ErrorMessage = "Postcode must be between 5 and 10 characters.")]
    [Display(Name = "Postcode")]
    public string Postcode { get; set; } = string.Empty;

    [StringLength(20, MinimumLength = 6, ErrorMessage = "Account Number must be between 6 and 20 characters.")]
    [RegularExpression(@"^\d{6,20}$", ErrorMessage = "Account Number must contain only digits.")]
    [Display(Name = "Account No")]
    public string AccountNo { get; set; } = string.Empty;

    [StringLength(11, MinimumLength = 6, ErrorMessage = "Sort Code must be between 6 and 11 characters.")]
    [RegularExpression(@"^\d{2}-?\d{2}-?\d{2}$", ErrorMessage = "Sort Code must be in format XX-XX-XX or XXXXXX.")]
    [Display(Name = "Sort Code")]
    public string SortCode { get; set; } = string.Empty;
}

public class AddressHistoryItem
{
    [Required(ErrorMessage = "Address is required.")]
    [StringLength(500, MinimumLength = 10, ErrorMessage = "Address must be between 10 and 500 characters.")]
    [Display(Name = "Address")]
    public string Address { get; set; } = string.Empty;

    [Required(ErrorMessage = "From date is required.")]
    [Display(Name = "From")]
    [DataType(DataType.Date)]
    public DateTime? From { get; set; }

    [Display(Name = "To")]
    [DataType(DataType.Date)]
    public DateTime? To { get; set; }

    [Required(ErrorMessage = "Landlord Name is required.")]
    [StringLength(100, MinimumLength = 2, ErrorMessage = "Landlord Name must be between 2 and 100 characters.")]
    [Display(Name = "Landlord Name")]
    public string LandlordName { get; set; } = string.Empty;

    [Required(ErrorMessage = "Landlord Telephone is required.")]
    [Phone(ErrorMessage = "Please enter a valid phone number.")]
    [StringLength(20, MinimumLength = 10, ErrorMessage = "Landlord Telephone must be between 10 and 20 characters.")]
    [Display(Name = "Landlord Tel")]
    public string LandlordTel { get; set; } = string.Empty;

    [Required(ErrorMessage = "Landlord Email is required.")]
    [EmailAddress(ErrorMessage = "Please enter a valid email address.")]
    [StringLength(254, ErrorMessage = "Email cannot exceed 254 characters.")]
    [Display(Name = "Landlord Email")]
    public string LandlordEmail { get; set; } = string.Empty;
}

public class Contacts
{
    [Required(ErrorMessage = "Next of Kin is required.")]
    [StringLength(100, MinimumLength = 2, ErrorMessage = "Next of Kin must be between 2 and 100 characters.")]
    [Display(Name = "Next of Kin")]
    public string NextOfKin { get; set; } = string.Empty;

    [Required(ErrorMessage = "Relationship is required.")]
    [StringLength(50, MinimumLength = 2, ErrorMessage = "Relationship must be between 2 and 50 characters.")]
    [Display(Name = "Relationship")]
    public string Relationship { get; set; } = string.Empty;

    [Required(ErrorMessage = "Address is required.")]
    [StringLength(500, MinimumLength = 10, ErrorMessage = "Address must be between 10 and 500 characters.")]
    [Display(Name = "Address")]
    public string Address { get; set; } = string.Empty;

    [Required(ErrorMessage = "Contact Number is required.")]
    [Phone(ErrorMessage = "Please enter a valid phone number.")]
    [StringLength(20, MinimumLength = 10, ErrorMessage = "Contact Number must be between 10 and 20 characters.")]
    [Display(Name = "Contact Number")]
    public string ContactNumber { get; set; } = string.Empty;
}

public class MedicalDetails
{
    [Display(Name = "GP Practice")]
    public string GpPractice { get; set; } = string.Empty;

    [Display(Name = "Doctor's Name")]
    public string DoctorName { get; set; } = string.Empty;

    [Display(Name = "Doctor's Address")]
    public string DoctorAddress { get; set; } = string.Empty;

    [Display(Name = "Doctor's Telephone No")]
    [Phone]
    public string DoctorTelephone { get; set; } = string.Empty;
}

public class Employment
{
    [StringLength(200, ErrorMessage = "Employer Name & Address cannot exceed 200 characters.")]
    [Display(Name = "Name & Address of Employer")]
    public string EmployerNameAddress { get; set; } = string.Empty;

    [StringLength(100, ErrorMessage = "Job Title cannot exceed 100 characters.")]
    [Display(Name = "Job Title")]
    public string JobTitle { get; set; } = string.Empty;

    [StringLength(100, ErrorMessage = "Manager's Name cannot exceed 100 characters.")]
    [Display(Name = "Manager's Name")]
    public string ManagerName { get; set; } = string.Empty;

    [Phone(ErrorMessage = "Please enter a valid phone number.")]
    [StringLength(20, ErrorMessage = "Manager's Telephone cannot exceed 20 characters.")]
    [Display(Name = "Manager's Tel")]
    public string ManagerTel { get; set; } = string.Empty;

    [EmailAddress(ErrorMessage = "Please enter a valid email address.")]
    [StringLength(254, ErrorMessage = "Manager's Email cannot exceed 254 characters.")]
    [Display(Name = "Manager's Email")]
    public string ManagerEmail { get; set; } = string.Empty;

    [Display(Name = "Date of Employment")]
    [DataType(DataType.Date)]
    public DateTime? DateOfEmployment { get; set; }

    [StringLength(50, ErrorMessage = "Present Salary cannot exceed 50 characters.")]
    [Display(Name = "Present Salary")]
    public string PresentSalary { get; set; } = string.Empty;
}

public class PassportDetails
{
    [Display(Name = "Passport Number")]
    public string PassportNumber { get; set; } = string.Empty;

    [Display(Name = "Date of Issue")]
    [DataType(DataType.Date)]
    public DateTime? DateOfIssue { get; set; }

    [Display(Name = "Place of Issue")]
    public string PlaceOfIssue { get; set; } = string.Empty;
}

public class CurrentLivingArrangement
{
    [Display(Name = "Does landlord know you are leaving?")]
    public bool LandlordKnows { get; set; }

    [Display(Name = "Notice End Date")]
    [DataType(DataType.Date)]
    public DateTime? NoticeEndDate { get; set; }

    [Display(Name = "Reason for Leaving")]
    public string ReasonLeaving { get; set; } = string.Empty;

    [Display(Name = "Will landlord give reference?")]
    public bool LandlordReference { get; set; }

    public LandlordContact LandlordContact { get; set; } = new();
}

public class Other
{
    public Pets Pets { get; set; } = new();

    [Display(Name = "Do you smoke?")]
    public bool Smoke { get; set; }

    public Coliving Coliving { get; set; } = new();
}

public class OccupationAgreement
{
    [Display(Name = "I agree to single occupancy terms")]
    public bool SingleOccupancyAgree { get; set; }

    [Display(Name = "I agree to HMO terms and conditions")]
    public bool HmoTermsAgree { get; set; }

    [Display(Name = "I will not allow unlisted occupants")]
    public bool NoUnlistedOccupants { get; set; }

    [Display(Name = "I agree to no smoking policy")]
    public bool NoSmoking { get; set; }

    [Display(Name = "I agree to use kitchen for cooking only")]
    public bool KitchenCookingOnly { get; set; }
}

public class ConsentAndDeclaration
{
    [MustBeTrue(ErrorMessage = "You must consent to the processing of your personal data to submit this form.")]
    [Display(Name = "I consent to the processing of my personal data")]
    public bool ConsentGiven { get; set; }

    [Required(ErrorMessage = "Signature is required.")]
    [Display(Name = "Signature")]
    public string Signature { get; set; } = string.Empty;

    [Required(ErrorMessage = "Date is required.")]
    [Display(Name = "Date")]
    [DataType(DataType.Date)]
    public DateTime? Date { get; set; }

    [Required(ErrorMessage = "Print Name is required.")]
    [Display(Name = "Print Name")]
    public string PrintName { get; set; } = string.Empty;

    public Declaration Declaration { get; set; } = new();

    [Required(ErrorMessage = "Declaration Signature is required.")]
    [Display(Name = "Declaration Signature")]
    public string DeclarationSignature { get; set; } = string.Empty;

    [Required(ErrorMessage = "Declaration Date is required.")]
    [Display(Name = "Declaration Date")]
    [DataType(DataType.Date)]
    public DateTime? DeclarationDate { get; set; }

    [Required(ErrorMessage = "Declaration Print Name is required.")]
    [Display(Name = "Declaration Print Name")]
    public string DeclarationPrintName { get; set; } = string.Empty;
}

// Nested classes
public class OtherNames
{
    [Display(Name = "Have you been known by any other name?")]
    public bool HasOtherNames { get; set; }

    [StringLength(200, ErrorMessage = "Details cannot exceed 200 characters.")]
    [Display(Name = "Details")]
    public string Details { get; set; } = string.Empty;
}

public class MedicalCondition
{
    [Display(Name = "Medical condition other residents need to know?")]
    public bool HasCondition { get; set; }

    [StringLength(500, ErrorMessage = "Details cannot exceed 500 characters.")]
    [Display(Name = "Details")]
    public string Details { get; set; } = string.Empty;
}

public class LandlordContact
{
    [StringLength(100, ErrorMessage = "Name cannot exceed 100 characters.")]
    [Display(Name = "Name")]
    public string Name { get; set; } = string.Empty;

    [StringLength(500, ErrorMessage = "Address cannot exceed 500 characters.")]
    [Display(Name = "Address")]
    public string Address { get; set; } = string.Empty;

    [Phone(ErrorMessage = "Please enter a valid phone number.")]
    [StringLength(20, ErrorMessage = "Telephone cannot exceed 20 characters.")]
    [Display(Name = "Tel")]
    public string Tel { get; set; } = string.Empty;

    [EmailAddress(ErrorMessage = "Please enter a valid email address.")]
    [StringLength(254, ErrorMessage = "Email cannot exceed 254 characters.")]
    [Display(Name = "Email")]
    public string Email { get; set; } = string.Empty;
}

public class Pets
{
    [Display(Name = "Do you have pets?")]
    public bool HasPets { get; set; }

    [Display(Name = "Details")]
    public string Details { get; set; } = string.Empty;
}

public class Coliving
{
    [Display(Name = "Co-living preferences?")]
    public bool HasColiving { get; set; }

    [Display(Name = "Details")]
    public string Details { get; set; } = string.Empty;
}

public class Declaration
{
    [MustBeTrue(ErrorMessage = "You must declare this will be your main home.")]
    [Display(Name = "This will be my main home")]
    public bool MainHome { get; set; }

    [MustBeTrue(ErrorMessage = "You must give permission for enquiries to be made.")]
    [Display(Name = "I give permission for enquiries to be made")]
    public bool EnquiriesPermission { get; set; }

    [MustBeTrue(ErrorMessage = "You must certify no outstanding county court judgements.")]
    [Display(Name = "I certify no outstanding county court judgements")]
    public bool CertifyNoJudgements { get; set; }

    [MustBeTrue(ErrorMessage = "You must certify no housing-related debt.")]
    [Display(Name = "I certify no housing-related debt")]
    public bool CertifyNoHousingDebt { get; set; }

    [MustBeTrue(ErrorMessage = "You must certify no debt to previous landlords.")]
    [Display(Name = "I certify no debt to previous landlords")]
    public bool CertifyNoLandlordDebt { get; set; }

    [MustBeTrue(ErrorMessage = "You must certify no history of property abuse.")]
    [Display(Name = "I certify no history of property abuse")]
    public bool CertifyNoAbuse { get; set; }
}

// Enums
public enum Gender
{
    Male,
    Female
}

public enum RoomOccupancy
{
    [Display(Name = "Just You")]
    JustYou,
    [Display(Name = "You and Someone Else")]
    YouAndSomeoneElse
}

// Main form data model
public class FormData
{
    public TenantDetails TenantDetails { get; set; } = new();
    public BankDetails BankDetails { get; set; } = new();
    public List<AddressHistoryItem> AddressHistory { get; set; } = new() { new AddressHistoryItem() };
    public Contacts Contacts { get; set; } = new();
    public MedicalDetails MedicalDetails { get; set; } = new();
    public Employment Employment { get; set; } = new();
    
    [Display(Name = "Are circumstances likely to change?")]
    public string EmploymentChange { get; set; } = string.Empty;
    
    public PassportDetails PassportDetails { get; set; } = new();
    public CurrentLivingArrangement CurrentLivingArrangement { get; set; } = new();
    public Other Other { get; set; } = new();
    public OccupationAgreement OccupationAgreement { get; set; } = new();
    public ConsentAndDeclaration ConsentAndDeclaration { get; set; } = new();
}