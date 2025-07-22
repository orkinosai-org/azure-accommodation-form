using System.ComponentModel.DataAnnotations;

namespace BlazorApp.Models;

public class TenantDetails
{
    [Required]
    [Display(Name = "Full Name")]
    public string FullName { get; set; } = string.Empty;

    [Required]
    [Display(Name = "Date of Birth")]
    [DataType(DataType.Date)]
    public DateTime? DateOfBirth { get; set; }

    [Display(Name = "Place of Birth")]
    public string PlaceOfBirth { get; set; } = string.Empty;

    [Required]
    [EmailAddress]
    [Display(Name = "Email")]
    public string Email { get; set; } = string.Empty;

    [Required]
    [Phone]
    [Display(Name = "Telephone")]
    public string Telephone { get; set; } = string.Empty;

    [Display(Name = "Employer's Name")]
    public string EmployersName { get; set; } = string.Empty;

    [Display(Name = "Gender")]
    public Gender? Gender { get; set; }

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
    [Display(Name = "Bank Name")]
    public string BankName { get; set; } = string.Empty;

    [Display(Name = "Postcode")]
    public string Postcode { get; set; } = string.Empty;

    [Display(Name = "Account No")]
    public string AccountNo { get; set; } = string.Empty;

    [Display(Name = "Sort Code")]
    public string SortCode { get; set; } = string.Empty;
}

public class AddressHistoryItem
{
    [Display(Name = "Address")]
    public string Address { get; set; } = string.Empty;

    [Display(Name = "From")]
    [DataType(DataType.Date)]
    public DateTime? From { get; set; }

    [Display(Name = "To")]
    [DataType(DataType.Date)]
    public DateTime? To { get; set; }

    [Display(Name = "Landlord Name")]
    public string LandlordName { get; set; } = string.Empty;

    [Display(Name = "Landlord Tel")]
    [Phone]
    public string LandlordTel { get; set; } = string.Empty;

    [Display(Name = "Landlord Email")]
    [EmailAddress]
    public string LandlordEmail { get; set; } = string.Empty;
}

public class Contacts
{
    [Display(Name = "Next of Kin")]
    public string NextOfKin { get; set; } = string.Empty;

    [Display(Name = "Relationship")]
    public string Relationship { get; set; } = string.Empty;

    [Display(Name = "Address")]
    public string Address { get; set; } = string.Empty;

    [Display(Name = "Contact Number")]
    [Phone]
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

    [Display(Name = "Doctor's Telephone")]
    [Phone]
    public string DoctorTelephone { get; set; } = string.Empty;
}

public class Employment
{
    [Display(Name = "Employer Name")]
    public string EmployerName { get; set; } = string.Empty;

    [Display(Name = "Employer Address")]
    public string EmployerAddress { get; set; } = string.Empty;

    [Display(Name = "Job Title")]
    public string JobTitle { get; set; } = string.Empty;

    [Display(Name = "Manager's Name")]
    public string ManagerName { get; set; } = string.Empty;

    [Display(Name = "Manager's Tel")]
    [Phone]
    public string ManagerTel { get; set; } = string.Empty;

    [Display(Name = "Manager's Email")]
    [EmailAddress]
    public string ManagerEmail { get; set; } = string.Empty;

    [Display(Name = "Date of Employment")]
    [DataType(DataType.Date)]
    public DateTime? DateOfEmployment { get; set; }

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
    [Display(Name = "I consent to the processing of my personal data")]
    public bool ConsentGiven { get; set; }

    [Display(Name = "Signature")]
    public string Signature { get; set; } = string.Empty;

    [Display(Name = "Date")]
    [DataType(DataType.Date)]
    public DateTime? Date { get; set; }

    [Display(Name = "Print Name")]
    public string PrintName { get; set; } = string.Empty;

    public Declaration Declaration { get; set; } = new();

    [Display(Name = "Declaration Signature")]
    public string DeclarationSignature { get; set; } = string.Empty;

    [Display(Name = "Declaration Date")]
    [DataType(DataType.Date)]
    public DateTime? DeclarationDate { get; set; }

    [Display(Name = "Declaration Print Name")]
    public string DeclarationPrintName { get; set; } = string.Empty;
}

// Nested classes
public class OtherNames
{
    [Display(Name = "Have you been known by any other name?")]
    public bool HasOtherNames { get; set; }

    [Display(Name = "Details")]
    public string Details { get; set; } = string.Empty;
}

public class MedicalCondition
{
    [Display(Name = "Medical condition other residents need to know?")]
    public bool HasCondition { get; set; }

    [Display(Name = "Details")]
    public string Details { get; set; } = string.Empty;
}

public class LandlordContact
{
    [Display(Name = "Name")]
    public string Name { get; set; } = string.Empty;

    [Display(Name = "Address")]
    public string Address { get; set; } = string.Empty;

    [Display(Name = "Tel")]
    [Phone]
    public string Tel { get; set; } = string.Empty;

    [Display(Name = "Email")]
    [EmailAddress]
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
    [Display(Name = "This will be my main home")]
    public bool MainHome { get; set; }

    [Display(Name = "I give permission for enquiries to be made")]
    public bool EnquiriesPermission { get; set; }

    [Display(Name = "I certify no outstanding county court judgements")]
    public bool CertifyNoJudgements { get; set; }

    [Display(Name = "I certify no housing-related debt")]
    public bool CertifyNoHousingDebt { get; set; }

    [Display(Name = "I certify no debt to previous landlords")]
    public bool CertifyNoLandlordDebt { get; set; }

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