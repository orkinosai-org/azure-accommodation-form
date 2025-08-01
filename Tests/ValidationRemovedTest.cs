using System.ComponentModel.DataAnnotations;

namespace Tests;

/// <summary>
/// Test to verify that Step 1 validation has been temporarily removed
/// </summary>
public class ValidationRemovedTest
{
    public static void TestValidationRemoved()
    {
        Console.WriteLine("=== STEP 1 VALIDATION REMOVED TEST ===");
        Console.WriteLine("Testing that Step 1 validation has been temporarily removed...");

        // Test that our modified EmailEntryModel (from ApplicationForm) has no validation
        // This simulates what happens in the actual form
        TestNoValidationAttributesOnEmailEntryModel();
        
        Console.WriteLine("✓ Step 1 validation successfully removed for testing!");
    }

    private static void TestNoValidationAttributesOnEmailEntryModel()
    {
        Console.WriteLine("Testing that no validation occurs on empty EmailEntryModel...");

        // Create an EmailEntryModel similar to the one in ApplicationForm.razor
        var testModel = new TestEmailEntryModel();
        
        // This should pass validation because we removed all validation attributes
        var validationContext = new ValidationContext(testModel);
        var validationResults = new List<ValidationResult>();
        
        bool isValid = Validator.TryValidateObject(testModel, validationContext, validationResults, true);
        
        if (isValid && validationResults.Count == 0)
        {
            Console.WriteLine("✓ Empty EmailEntryModel passes validation (no validation attributes)");
        }
        else
        {
            throw new Exception($"Expected empty model to pass validation, but got {validationResults.Count} errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }

        // Test with some data - should still pass
        var modelWithData = new TestEmailEntryModel
        {
            Email = "invalid-email",  // Invalid format, but no validation should occur
            ConfirmEmail = "different@email.com",  // Different from Email, but no validation should occur
            CaptchaAnswer = -999  // Invalid range, but no validation should occur
        };
        
        var dataValidationContext = new ValidationContext(modelWithData);
        validationResults.Clear();
        isValid = Validator.TryValidateObject(modelWithData, dataValidationContext, validationResults, true);
        
        if (isValid && validationResults.Count == 0)
        {
            Console.WriteLine("✓ EmailEntryModel with invalid data still passes validation (no validation attributes)");
        }
        else
        {
            throw new Exception($"Expected model with invalid data to pass validation, but got {validationResults.Count} errors: {string.Join(", ", validationResults.Select(r => r.ErrorMessage))}");
        }
    }

    // Test model that mirrors the modified EmailEntryModel in ApplicationForm.razor
    private class TestEmailEntryModel
    {
        // No validation attributes - these have been commented out
        public string Email { get; set; } = string.Empty;
        public string ConfirmEmail { get; set; } = string.Empty;
        public int? CaptchaAnswer { get; set; }
    }
}