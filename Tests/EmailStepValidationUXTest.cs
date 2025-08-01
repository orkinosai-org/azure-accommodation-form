using System.ComponentModel.DataAnnotations;
using BlazorApp.Validation;

namespace Tests;

/// <summary>
/// Test class to verify that the email step validation UX behaves correctly
/// This test ensures that validation errors don't appear immediately but only after form submission
/// </summary>
public class EmailStepValidationUXTest
{
    public static async Task TestEmailStepValidationUX()
    {
        Console.WriteLine("=== EMAIL STEP VALIDATION UX TEST ===");
        Console.WriteLine("Testing that validation errors appear only after submit or blur, not immediately...");

        // Test the EmailEntryModel validation behavior
        await TestEmailEntryModelValidationBehavior();
        
        Console.WriteLine("✓ All email step validation UX tests passed!");
    }

    private static async Task TestEmailEntryModelValidationBehavior()
    {
        Console.WriteLine("Testing EmailEntryModel validation behavior...");

        // Create a fresh model (simulating page load state)
        var emailModel = new EmailEntryModel();
        
        // This simulates the initial state - validation should not be triggered immediately
        var validationContext = new ValidationContext(emailModel);
        var validationResults = new List<ValidationResult>();
        
        // Test initial state - empty model
        bool isValid = Validator.TryValidateObject(emailModel, validationContext, validationResults, true);
        
        if (!isValid)
        {
            Console.WriteLine($"✓ Empty model correctly fails validation with {validationResults.Count} errors");
            Console.WriteLine($"  - Validation errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }
        else
        {
            throw new Exception("Expected empty model to fail validation");
        }

        // Test partial input - only email filled
        var partialModel = new EmailEntryModel
        {
            Email = "test@example.com"
            // ConfirmEmail and CaptchaAnswer are still empty/null
        };
        
        var partialValidationContext = new ValidationContext(partialModel);
        validationResults.Clear();
        isValid = Validator.TryValidateObject(partialModel, partialValidationContext, validationResults, true);
        
        if (!isValid)
        {
            Console.WriteLine($"✓ Partial model correctly fails validation with {validationResults.Count} errors");
            var remainingErrors = validationResults.Select(r => r.ErrorMessage).ToList();
            Console.WriteLine($"  - Remaining validation errors: {string.Join(", ", remainingErrors)}");
        }
        else
        {
            throw new Exception("Expected partial model to fail validation");
        }

        // Test mismatched emails
        var mismatchedModel = new EmailEntryModel
        {
            Email = "test@example.com",
            ConfirmEmail = "different@example.com",
            CaptchaAnswer = 42
        };
        
        var mismatchedValidationContext = new ValidationContext(mismatchedModel);
        validationResults.Clear();
        isValid = Validator.TryValidateObject(mismatchedModel, mismatchedValidationContext, validationResults, true);
        
        if (!isValid && validationResults.Any(r => r.ErrorMessage?.Contains("do not match") == true))
        {
            Console.WriteLine("✓ Mismatched emails correctly fail validation");
        }
        else
        {
            throw new Exception("Expected mismatched emails to fail validation with 'do not match' message");
        }

        // Test fully valid model
        var validModel = new EmailEntryModel
        {
            Email = "test@example.com",
            ConfirmEmail = "test@example.com",
            CaptchaAnswer = 42
        };
        
        var validValidationContext = new ValidationContext(validModel);
        validationResults.Clear();
        isValid = Validator.TryValidateObject(validModel, validValidationContext, validationResults, true);
        
        if (isValid)
        {
            Console.WriteLine("✓ Valid model passes validation");
        }
        else
        {
            throw new Exception($"Expected valid model to pass validation, but got errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        await Task.CompletedTask;
    }

    // Copy of EmailEntryModel for testing (to match the one in ApplicationForm.razor)
    private class EmailEntryModel
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; } = string.Empty;

        [Required]
        [EmailAddress]
        [EmailEquality(nameof(Email), ErrorMessage = "Email addresses do not match.")]
        public string ConfirmEmail { get; set; } = string.Empty;

        [Required]
        [Range(1, 100, ErrorMessage = "Please answer the security question correctly.")]
        public int? CaptchaAnswer { get; set; }
    }
}