using System.ComponentModel.DataAnnotations;

namespace BlazorApp.Validation;

public class EmailEqualityAttribute : ValidationAttribute
{
    private readonly string _comparisonProperty;

    public EmailEqualityAttribute(string comparisonProperty)
    {
        _comparisonProperty = comparisonProperty;
    }

    protected override ValidationResult? IsValid(object? value, ValidationContext validationContext)
    {
        var property = validationContext.ObjectType.GetProperty(_comparisonProperty);
        if (property == null)
        {
            return new ValidationResult($"Unknown property: {_comparisonProperty}");
        }

        var comparisonValue = property.GetValue(validationContext.ObjectInstance);
        
        if (!Equals(value, comparisonValue))
        {
            return new ValidationResult(ErrorMessage ?? "Email addresses do not match.");
        }

        return ValidationResult.Success;
    }
}