using System.ComponentModel.DataAnnotations;
using BlazorApp.Models;
using BlazorApp.Validation;

namespace Tests;

/// <summary>
/// Test class to verify consent and declaration validation functionality
/// This test ensures that the required validation attributes work correctly for critical form fields
/// </summary>
public class ConsentValidationTest
{
    public static async Task TestConsentValidation()
    {
        Console.WriteLine("=== CONSENT VALIDATION TEST ===");
        Console.WriteLine("Testing consent and declaration validation functionality...");

        // Test consent validation
        await TestConsentRequiredValidation();
        
        // Test declaration validation
        await TestDeclarationRequiredValidation();
        
        // Test signature fields validation
        await TestSignatureFieldsValidation();
        
        Console.WriteLine("✓ All consent validation tests passed!");
    }

    private static async Task TestConsentRequiredValidation()
    {
        Console.WriteLine("Testing ConsentGiven required validation...");

        // Test with consent given (should pass)
        var validConsent = new ConsentAndDeclaration
        {
            ConsentGiven = true,
            Signature = "Test User",
            Date = DateTime.Today,
            PrintName = "Test User",
            DeclarationSignature = "Test User",
            DeclarationDate = DateTime.Today,
            DeclarationPrintName = "Test User",
            Declaration = new Declaration
            {
                MainHome = true,
                EnquiriesPermission = true,
                CertifyNoJudgements = true,
                CertifyNoHousingDebt = true,
                CertifyNoLandlordDebt = true,
                CertifyNoAbuse = true
            }
        };

        var validationContext = new ValidationContext(validConsent);
        var validationResults = new List<ValidationResult>();

        bool isValid = Validator.TryValidateObject(validConsent, validationContext, validationResults, true);

        if (isValid)
        {
            Console.WriteLine("✓ Valid consent (ConsentGiven=true) passed validation");
        }
        else
        {
            Console.WriteLine($"Validation errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
            throw new Exception($"Expected valid consent to pass validation, but got errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test with consent not given (should fail)
        var invalidConsent = new ConsentAndDeclaration
        {
            ConsentGiven = false, // This should cause validation failure
            Signature = "Test User",
            Date = DateTime.Today,
            PrintName = "Test User",
            DeclarationSignature = "Test User",
            DeclarationDate = DateTime.Today,
            DeclarationPrintName = "Test User",
            Declaration = new Declaration
            {
                MainHome = true,
                EnquiriesPermission = true,
                CertifyNoJudgements = true,
                CertifyNoHousingDebt = true,
                CertifyNoLandlordDebt = true,
                CertifyNoAbuse = true
            }
        };

        var invalidValidationContext = new ValidationContext(invalidConsent);
        validationResults.Clear();
        isValid = Validator.TryValidateObject(invalidConsent, invalidValidationContext, validationResults, true);

        if (!isValid && validationResults.Any(r => r.ErrorMessage?.Contains("consent") == true))
        {
            Console.WriteLine("✓ Invalid consent (ConsentGiven=false) correctly failed validation");
        }
        else
        {
            Console.WriteLine($"Validation results: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
            Console.WriteLine($"IsValid: {isValid}, ErrorCount: {validationResults.Count}");
            throw new Exception("Expected ConsentGiven=false to fail validation with consent-related error message");
        }

        await Task.CompletedTask;
    }

    private static async Task TestDeclarationRequiredValidation()
    {
        Console.WriteLine("Testing Declaration required validation...");

        // Test with all declarations true (should pass)
        var validDeclaration = new Declaration
        {
            MainHome = true,
            EnquiriesPermission = true,
            CertifyNoJudgements = true,
            CertifyNoHousingDebt = true,
            CertifyNoLandlordDebt = true,
            CertifyNoAbuse = true
        };

        var validationContext = new ValidationContext(validDeclaration);
        var validationResults = new List<ValidationResult>();

        bool isValid = Validator.TryValidateObject(validDeclaration, validationContext, validationResults, true);

        if (isValid)
        {
            Console.WriteLine("✓ Valid declaration (all fields true) passed validation");
        }
        else
        {
            throw new Exception($"Expected valid declaration to pass validation, but got errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test with missing declarations (should fail)
        var invalidDeclaration = new Declaration
        {
            MainHome = false, // This should cause validation failure
            EnquiriesPermission = false,
            CertifyNoJudgements = false,
            CertifyNoHousingDebt = false,
            CertifyNoLandlordDebt = false,
            CertifyNoAbuse = false
        };

        var invalidValidationContext = new ValidationContext(invalidDeclaration);
        validationResults.Clear();
        isValid = Validator.TryValidateObject(invalidDeclaration, invalidValidationContext, validationResults, true);

        if (!isValid && validationResults.Count == 6) // Should have 6 validation errors, one for each required field
        {
            Console.WriteLine($"✓ Invalid declaration correctly failed validation with {validationResults.Count} errors");
        }
        else
        {
            throw new Exception($"Expected declaration with all false values to fail validation with 6 errors, but got {validationResults.Count} errors");
        }

        await Task.CompletedTask;
    }

    private static async Task TestSignatureFieldsValidation()
    {
        Console.WriteLine("Testing signature fields validation...");

        // Test with missing signature fields (should fail)
        var invalidConsent = new ConsentAndDeclaration
        {
            ConsentGiven = true,
            Signature = "", // Missing required field
            Date = null, // Missing required field
            PrintName = "", // Missing required field
            DeclarationSignature = "", // Missing required field
            DeclarationDate = null, // Missing required field
            DeclarationPrintName = "", // Missing required field
            Declaration = new Declaration
            {
                MainHome = true,
                EnquiriesPermission = true,
                CertifyNoJudgements = true,
                CertifyNoHousingDebt = true,
                CertifyNoLandlordDebt = true,
                CertifyNoAbuse = true
            }
        };

        var validationContext = new ValidationContext(invalidConsent);
        var validationResults = new List<ValidationResult>();

        bool isValid = Validator.TryValidateObject(invalidConsent, validationContext, validationResults, true);

        if (!isValid)
        {
            var signatureErrors = validationResults.Where(r => 
                r.ErrorMessage?.Contains("Signature") == true ||
                r.ErrorMessage?.Contains("Date") == true ||
                r.ErrorMessage?.Contains("Print Name") == true
            ).ToList();

            if (signatureErrors.Count >= 4) // Should have at least 4 signature-related validation errors
            {
                Console.WriteLine($"✓ Missing signature fields correctly failed validation with {signatureErrors.Count} signature-related errors");
            }
            else
            {
                throw new Exception($"Expected missing signature fields to fail validation with at least 4 signature-related errors, but got {signatureErrors.Count}");
            }
        }
        else
        {
            throw new Exception("Expected missing signature fields to fail validation");
        }

        await Task.CompletedTask;
    }
}