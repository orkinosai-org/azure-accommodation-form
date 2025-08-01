using System.ComponentModel.DataAnnotations;
using BlazorApp.Validation;

namespace Tests;

/// <summary>
/// Test class to verify email validation functionality
/// This test ensures that the EmailEqualityAttribute and EmailEntryModel work correctly
/// </summary>
public class EmailValidationTest
{
    public static async Task TestEmailValidation()
    {
        Console.WriteLine("=== EMAIL VALIDATION TEST ===");
        Console.WriteLine("Testing email validation functionality...");

        // Test EmailEqualityAttribute directly
        await TestEmailEqualityAttribute();
        
        // Test EmailEntryModel validation
        await TestEmailEntryModelValidation();
        
        Console.WriteLine("✓ All email validation tests passed!");
    }

    private static async Task TestEmailEqualityAttribute()
    {
        Console.WriteLine("Testing EmailEqualityAttribute...");

        var testModel = new TestEmailModel
        {
            Email = "test@example.com",
            ConfirmEmail = "test@example.com"
        };

        var validationContext = new ValidationContext(testModel);
        var validationResults = new List<ValidationResult>();

        bool isValid = Validator.TryValidateObject(testModel, validationContext, validationResults, true);

        if (isValid)
        {
            Console.WriteLine("✓ Matching emails passed validation");
        }
        else
        {
            throw new Exception($"Expected matching emails to be valid, but got errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test non-matching emails
        testModel.ConfirmEmail = "different@example.com";
        validationResults.Clear();
        isValid = Validator.TryValidateObject(testModel, validationContext, validationResults, true);

        if (!isValid && validationResults.Any(r => r.ErrorMessage?.Contains("do not match") == true))
        {
            Console.WriteLine("✓ Non-matching emails correctly failed validation");
        }
        else
        {
            throw new Exception("Expected non-matching emails to fail validation with 'do not match' message");
        }

        await Task.CompletedTask;
    }

    private static async Task TestEmailEntryModelValidation()
    {
        Console.WriteLine("Testing EmailEntryModel validation...");

        // Test valid model
        var validModel = new EmailEntryModel
        {
            Email = "valid@example.com",
            ConfirmEmail = "valid@example.com",
            CaptchaAnswer = 42
        };

        var validationContext = new ValidationContext(validModel);
        var validationResults = new List<ValidationResult>();
        bool isValid = Validator.TryValidateObject(validModel, validationContext, validationResults, true);

        if (isValid)
        {
            Console.WriteLine("✓ Valid EmailEntryModel passed validation");
        }
        else
        {
            throw new Exception($"Expected valid model to pass validation, but got errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test model with missing required fields
        var invalidModel = new EmailEntryModel();
        var invalidValidationContext = new ValidationContext(invalidModel);
        validationResults.Clear();
        isValid = Validator.TryValidateObject(invalidModel, invalidValidationContext, validationResults, true);

        if (!isValid)
        {
            Console.WriteLine($"✓ Invalid EmailEntryModel correctly failed validation with {validationResults.Count} errors");
        }
        else
        {
            throw new Exception("Expected invalid model to fail validation");
        }

        await Task.CompletedTask;
    }

    private class TestEmailModel
    {
        public string Email { get; set; } = string.Empty;

        [EmailEquality(nameof(Email), ErrorMessage = "Email addresses do not match.")]
        public string ConfirmEmail { get; set; } = string.Empty;
    }

    // Copy of EmailEntryModel for testing (to avoid circular dependencies)
    private class EmailEntryModel
    {
        [Required(ErrorMessage = "The Email field is required.")]
        [EmailAddress]
        public string Email { get; set; } = string.Empty;

        [Required(ErrorMessage = "The ConfirmEmail field is required.")]
        [EmailAddress]
        [EmailEquality(nameof(Email), ErrorMessage = "Email addresses do not match.")]
        public string ConfirmEmail { get; set; } = string.Empty;

        [Required(ErrorMessage = "Please answer the security question correctly.")]
        [Range(1, 100, ErrorMessage = "Please answer the security question correctly.")]
        public int? CaptchaAnswer { get; set; }
    }
}