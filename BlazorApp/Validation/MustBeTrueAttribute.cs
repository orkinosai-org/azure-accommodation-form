using System.ComponentModel.DataAnnotations;

namespace BlazorApp.Validation;

/// <summary>
/// Validation attribute that requires a boolean property to be true.
/// This is used for consent checkboxes and declaration checkboxes that must be checked.
/// </summary>
public class MustBeTrueAttribute : ValidationAttribute
{
    public override bool IsValid(object? value)
    {
        if (value is bool boolValue)
        {
            return boolValue == true;
        }
        
        // If value is not a boolean, consider it invalid
        return false;
    }

    public override string FormatErrorMessage(string name)
    {
        return ErrorMessage ?? $"The {name} field must be checked.";
    }
}