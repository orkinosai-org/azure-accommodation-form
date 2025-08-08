using System.ComponentModel.DataAnnotations;
using BlazorApp.Models;

namespace Tests;

/// <summary>
/// Test class to verify form validation functionality
/// This test ensures that form models validate correctly according to business rules
/// </summary>
public class FormValidationTest
{
    public static async Task TestFormValidation()
    {
        Console.WriteLine("=== FORM VALIDATION TEST ===");
        Console.WriteLine("Testing form validation functionality...");

        // Test validation rules
        await TestTenantDetailsValidation();
        await TestBankDetailsValidation();
        await TestAddressHistoryValidation();
        await TestContactsValidation();
        await TestConsentValidation();
        await TestCompleteFormValidation();

        Console.WriteLine("✅ All form validation tests passed!");
    }

    private static List<ValidationResult> ValidateModel(object model)
    {
        var validationResults = new List<ValidationResult>();
        var context = new ValidationContext(model, null, null);
        Validator.TryValidateObject(model, context, validationResults, true);
        return validationResults;
    }

    private static async Task TestTenantDetailsValidation()
    {
        Console.WriteLine("Testing TenantDetails validation...");

        // Test valid data
        var validTenant = new TenantDetails
        {
            FullName = "John Doe",
            DateOfBirth = DateTime.Now.AddYears(-25),
            Email = "john.doe@example.com",
            Telephone = "+44 123 456 7890",
            NiNumber = "AB123456C"
        };

        var validationResults = ValidateModel(validTenant);
        if (validationResults.Any())
        {
            throw new Exception($"Valid TenantDetails failed validation: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test invalid data
        var invalidTenant = new TenantDetails
        {
            FullName = "A", // Too short
            Email = "invalid-email", // Invalid format
            Telephone = "123", // Too short
            NiNumber = "AVERYLONGNUMBERTHATISTOOLONG" // Too long
        };

        validationResults = ValidateModel(invalidTenant);
        if (!validationResults.Any())
        {
            throw new Exception("Invalid TenantDetails should have failed validation");
        }

        var expectedErrors = new[]
        {
            "Full Name must be between 2 and 100 characters",
            "Date of Birth is required",
            "valid email address",
            "Telephone must be between 10 and 20 characters",
            "NI Number must be between 9 and 13 characters"
        };

        foreach (var expectedError in expectedErrors)
        {
            if (!validationResults.Any(r => r.ErrorMessage!.Contains(expectedError)))
            {
                throw new Exception($"Expected validation error not found: {expectedError}");
            }
        }

        Console.WriteLine("✅ TenantDetails validation tests passed");
    }

    private static async Task TestBankDetailsValidation()
    {
        Console.WriteLine("Testing BankDetails validation...");

        // Test valid data
        var validBank = new BankDetails
        {
            BankName = "HSBC Bank",
            Postcode = "SW1A 1AA",
            AccountNo = "12345678",
            SortCode = "12-34-56"
        };

        var validationResults = ValidateModel(validBank);
        if (validationResults.Any())
        {
            throw new Exception($"Valid BankDetails failed validation: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test invalid account number
        var invalidBank = new BankDetails
        {
            AccountNo = "ABC123", // Contains letters
            SortCode = "invalid" // Invalid format
        };

        validationResults = ValidateModel(invalidBank);
        if (!validationResults.Any())
        {
            throw new Exception("Invalid BankDetails should have failed validation");
        }

        var hasAccountError = validationResults.Any(r => r.ErrorMessage!.Contains("Account Number must contain only digits"));
        var hasSortCodeError = validationResults.Any(r => r.ErrorMessage!.Contains("Sort Code must be in format"));

        if (!hasAccountError || !hasSortCodeError)
        {
            throw new Exception("Expected BankDetails validation errors not found");
        }

        Console.WriteLine("✅ BankDetails validation tests passed");
    }

    private static async Task TestAddressHistoryValidation()
    {
        Console.WriteLine("Testing AddressHistory validation...");

        // Test valid address
        var validAddress = new AddressHistoryItem
        {
            Address = "123 Main Street, London, SW1A 1AA",
            From = DateTime.Now.AddYears(-2),
            LandlordName = "John Smith",
            LandlordTel = "+44 123 456 7890",
            LandlordEmail = "landlord@example.com"
        };

        var validationResults = ValidateModel(validAddress);
        if (validationResults.Any())
        {
            throw new Exception($"Valid AddressHistoryItem failed validation: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test invalid address
        var invalidAddress = new AddressHistoryItem
        {
            Address = "Short" // Too short
            // Missing required fields
        };

        validationResults = ValidateModel(invalidAddress);
        if (!validationResults.Any())
        {
            throw new Exception("Invalid AddressHistoryItem should have failed validation");
        }

        var expectedErrors = new[]
        {
            "Address must be between 10 and 500 characters",
            "From date is required",
            "Landlord Name is required",
            "Landlord Telephone is required",
            "Landlord Email is required"
        };

        foreach (var expectedError in expectedErrors)
        {
            if (!validationResults.Any(r => r.ErrorMessage!.Contains(expectedError)))
            {
                throw new Exception($"Expected validation error not found: {expectedError}");
            }
        }

        Console.WriteLine("✅ AddressHistory validation tests passed");
    }

    private static async Task TestContactsValidation()
    {
        Console.WriteLine("Testing Contacts validation...");

        // Test valid contacts
        var validContacts = new Contacts
        {
            NextOfKin = "Jane Doe",
            Relationship = "Sister",
            Address = "456 Oak Street, Manchester, M1 1AA",
            ContactNumber = "+44 987 654 3210"
        };

        var validationResults = ValidateModel(validContacts);
        if (validationResults.Any())
        {
            throw new Exception($"Valid Contacts failed validation: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test invalid contacts
        var invalidContacts = new Contacts
        {
            NextOfKin = "A", // Too short
            Relationship = "X", // Too short
            Address = "Short", // Too short
            ContactNumber = "123" // Too short
        };

        validationResults = ValidateModel(invalidContacts);
        if (!validationResults.Any())
        {
            throw new Exception("Invalid Contacts should have failed validation");
        }

        var expectedErrors = new[]
        {
            "Next of Kin must be between 2 and 100 characters",
            "Relationship must be between 2 and 50 characters",
            "Address must be between 10 and 500 characters",
            "Contact Number must be between 10 and 20 characters"
        };

        foreach (var expectedError in expectedErrors)
        {
            if (!validationResults.Any(r => r.ErrorMessage!.Contains(expectedError)))
            {
                throw new Exception($"Expected validation error not found: {expectedError}");
            }
        }

        Console.WriteLine("✅ Contacts validation tests passed");
    }

    private static async Task TestConsentValidation()
    {
        Console.WriteLine("Testing ConsentAndDeclaration validation...");

        // Test valid consent
        var validConsent = new ConsentAndDeclaration
        {
            ConsentGiven = true,
            Signature = "John Doe",
            Date = DateTime.Today,
            PrintName = "John Doe",
            Declaration = new Declaration
            {
                MainHome = true,
                EnquiriesPermission = true,
                CertifyNoJudgements = true,
                CertifyNoHousingDebt = true,
                CertifyNoLandlordDebt = true,
                CertifyNoAbuse = true
            },
            DeclarationSignature = "John Doe",
            DeclarationDate = DateTime.Today,
            DeclarationPrintName = "John Doe"
        };

        var validationResults = ValidateModel(validConsent);
        if (validationResults.Any())
        {
            throw new Exception($"Valid ConsentAndDeclaration failed validation: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test invalid consent (missing required consents)
        var invalidConsent = new ConsentAndDeclaration
        {
            ConsentGiven = false, // Must be true
            Declaration = new Declaration
            {
                MainHome = false, // Must be true
                EnquiriesPermission = false, // Must be true
                CertifyNoJudgements = false, // Must be true
                CertifyNoHousingDebt = false, // Must be true
                CertifyNoLandlordDebt = false, // Must be true
                CertifyNoAbuse = false // Must be true
            }
            // Missing required signature fields
        };

        validationResults = ValidateModel(invalidConsent);
        if (!validationResults.Any())
        {
            throw new Exception("Invalid ConsentAndDeclaration should have failed validation");
        }

        var hasConsentError = validationResults.Any(r => r.ErrorMessage!.Contains("You must consent to the processing"));
        var hasSignatureError = validationResults.Any(r => r.ErrorMessage!.Contains("Signature is required"));

        if (!hasConsentError || !hasSignatureError)
        {
            throw new Exception("Expected ConsentAndDeclaration validation errors not found");
        }

        Console.WriteLine("✅ ConsentAndDeclaration validation tests passed");
    }

    private static async Task TestCompleteFormValidation()
    {
        Console.WriteLine("Testing complete FormData validation...");

        // Test complete valid form
        var validForm = new FormData
        {
            TenantDetails = new TenantDetails
            {
                FullName = "John Doe",
                DateOfBirth = DateTime.Now.AddYears(-25),
                Email = "john.doe@example.com",
                Telephone = "+44 123 456 7890"
            },
            BankDetails = new BankDetails
            {
                BankName = "HSBC Bank",
                Postcode = "SW1A 1AA",
                AccountNo = "12345678",
                SortCode = "12-34-56"
            },
            AddressHistory = new List<AddressHistoryItem>
            {
                new AddressHistoryItem
                {
                    Address = "123 Main Street, London, SW1A 1AA",
                    From = DateTime.Now.AddYears(-2),
                    LandlordName = "John Smith",
                    LandlordTel = "+44 123 456 7890",
                    LandlordEmail = "landlord@example.com"
                }
            },
            Contacts = new Contacts
            {
                NextOfKin = "Jane Doe",
                Relationship = "Sister",
                Address = "456 Oak Street, Manchester, M1 1AA",
                ContactNumber = "+44 987 654 3210"
            },
            ConsentAndDeclaration = new ConsentAndDeclaration
            {
                ConsentGiven = true,
                Signature = "John Doe",
                Date = DateTime.Today,
                PrintName = "John Doe",
                Declaration = new Declaration
                {
                    MainHome = true,
                    EnquiriesPermission = true,
                    CertifyNoJudgements = true,
                    CertifyNoHousingDebt = true,
                    CertifyNoLandlordDebt = true,
                    CertifyNoAbuse = true
                },
                DeclarationSignature = "John Doe",
                DeclarationDate = DateTime.Today,
                DeclarationPrintName = "John Doe"
            }
        };

        var validationResults = ValidateModel(validForm);
        if (validationResults.Any())
        {
            throw new Exception($"Valid complete form failed validation: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        Console.WriteLine("✅ Complete FormData validation tests passed");
    }
}