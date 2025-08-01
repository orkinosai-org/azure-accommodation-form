# Step 1 Validation Removal - Revert Instructions

This document provides instructions for reverting the temporary changes made to remove Step 1 validation.

## Changes Made

### 1. ApplicationForm.razor - EmailEntryModel class (lines ~1207-1218)
**COMMENTED OUT:**
```csharp
// VALIDATION ATTRIBUTES COMMENTED OUT FOR TESTING
//[Required]
//[EmailAddress]
public string Email { get; set; } = string.Empty;

//[Required]
//[EmailAddress]
//[EmailEquality(nameof(Email), ErrorMessage = "Email addresses do not match.")]
public string ConfirmEmail { get; set; } = string.Empty;

//[Required]
//[Range(1, 100, ErrorMessage = "Please answer the security question correctly.")]
public int? CaptchaAnswer { get; set; }
```

**TO REVERT:** Uncomment the validation attributes by removing the `//` from each line.

### 2. ApplicationForm.razor - Validation error messages (lines ~25-67)
**COMMENTED OUT:** All validation message blocks like:
```html
@* VALIDATION COMMENTED OUT FOR TESTING
@if (emailSubmitAttempted && !IsValidEmail(emailModel.Email))
{
    <div class="validation-message">The Email field is required.</div>
}
...
*@
```

**TO REVERT:** Remove the `@* VALIDATION COMMENTED OUT FOR TESTING` and `*@` wrapper comments.

### 3. ApplicationForm.razor - InitializeForm method validation logic (lines ~927-943)
**COMMENTED OUT:**
```csharp
// VALIDATION COMMENTED OUT FOR TESTING - form will accept any input
// Perform manual validation since we removed DataAnnotationsValidator
/*
if (!IsValidEmailForm())
{
    return; // Validation errors will be shown due to emailSubmitAttempted = true
}

// Validate CAPTCHA
if (emailModel.CaptchaAnswer != captchaAnswer)
{
    ShowError("Security verification failed. Please try again.");
    GenerateNewCaptcha(); // Generate new CAPTCHA on failure
    return;
}
*/
```

**TO REVERT:** Remove the `/*` and `*/` comment blocks and the explanatory comment.

## Added Files (can be removed)
- `Tests/ValidationRemovedTest.cs` - Test confirming validation removal
- Updated `Tests/StartupWithoutAzureDiagnosticsTest.cs` to include the new test

## Result
After these changes:
- No validation errors appear on Step 1
- Form fields are fully editable
- Form attempts to proceed to API call even with invalid data
- Only backend API errors appear (like "Failed to initialize form")

## Easy Revert Command
1. Uncomment all validation attributes in EmailEntryModel
2. Remove the `@* VALIDATION COMMENTED OUT FOR TESTING ... *@` wrappers
3. Remove the `/* ... */` wrapper in InitializeForm method
4. Optional: Remove ValidationRemovedTest.cs and revert StartupWithoutAzureDiagnosticsTest.cs