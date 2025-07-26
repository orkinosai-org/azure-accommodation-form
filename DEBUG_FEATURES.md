# Debug Features for Azure Accommodation Form

This document describes the debug features added to assist with local debugging of email and blob storage issues.

## Overview

Debug logging has been added to all key services to provide visibility into:
- Configuration values used for email and blob storage
- Email message details before sending
- Blob upload details before uploading
- Local PDF copies for debugging

## Debug Output Location

All debug output is visible in:
- **Console output** (for immediate visibility during development)
- **ILogger output** (appears in VS2022 Output window and structured logs)
- **Local PDF files** (saved in `KitDocuments_Debug` directory)

## Services Enhanced

### 1. EmailService (`BlazorApp/Services/EmailService.cs`)

**Configuration Logging:**
- SMTP server, port, SSL settings
- Username and from email
- Password status (masked as `***CONFIGURED***` or `***NOT SET***`)

**Message Logging:**
- Email subject, from, to addresses
- Attachment count and names
- Recipient addresses

**Error Logging:**
- Detailed error messages with stack traces

### 2. BlobStorageService (`BlazorApp/Services/BlobStorageService.cs`)

**Configuration Logging:**
- Container name
- Connection string (with secrets masked)

**Upload Logging:**
- Blob name and target URI
- File size in bytes
- Submission ID

**Error Logging:**
- Detailed error messages with stack traces

### 3. PdfGenerationService (`BlazorApp/Services/PdfGenerationService.cs`)

**Generation Logging:**
- Submission details (ID, timestamp, client IP)
- Tenant information
- PDF file size

**Local Debug Storage:**
- Saves PDF copy to `KitDocuments_Debug/[SubmissionId]_[Timestamp]_debug.pdf`
- Creates directory automatically if it doesn't exist

### 4. FormService (`BlazorApp/Services/FormService.cs`)

**Orchestration Logging:**
- Clear phase markers for PDF generation, blob upload, and email sending
- Submission tracking throughout the process

## Example Debug Output

```
=== PDF GENERATION DEBUG ===
Submission ID: test-submission-123
Submission Time: 2024-01-15 10:30:00 UTC
Client IP: 192.168.1.100
Tenant Name: John Doe
Tenant Email: john@example.com

=== PDF SAVED LOCALLY ===
Debug PDF saved to: /path/to/project/KitDocuments_Debug/test-submission-123_20240115_103000_debug.pdf

=== EMAIL DEBUG INFO ===
SMTP Server: smtp.gmail.com
SMTP Port: 587
Use SSL: True
Username: noreply@company.com
Password: ***CONFIGURED***
From Email: noreply@company.com
From Name: Company Name
Company Email: company@company.com

=== EMAIL MESSAGE DEBUG ===
Subject: Accommodation Application Submitted
From: "Company Name" <noreply@company.com>
To: john@example.com
Attachment count: 1
Attachment names: John_Doe_Application_Form_15012024_1030.pdf

=== BLOB STORAGE DEBUG INFO ===
Container Name: form-submissions
Connection String: DefaultEndpointsProtocol=https;AccountName=storageaccount;AccountKey=***MASKED***;EndpointSuffix=core.windows.net

=== BLOB UPLOAD DEBUG ===
Blob Name: test-submission-123/John_Doe_Application_Form_15012024_1030.pdf
File Size: 52404 bytes
Submission ID: test-submission-123
Target URI: https://storageaccount.blob.core.windows.net/form-submissions/test-submission-123/John_Doe_Application_Form_15012024_1030.pdf
```

## Security Considerations

- **Passwords are masked** in all output as `***CONFIGURED***` or `***NOT SET***`
- **Connection string secrets are masked** using regex patterns
- **Personal data** in form submissions may appear in debug logs - review before sharing logs

## Removing Debug Code for Production

All debug code is marked with comments for easy removal:

```csharp
// DEBUG: Log configuration (production: remove this section)
Console.WriteLine("=== EMAIL DEBUG INFO ===");
// ... debug code here ...

// DEBUG: Enhanced error logging (production: keep but remove DEBUG prefix)
```

To prepare for production:
1. Search for `// DEBUG:` comments
2. Remove sections marked `(production: remove this section)`
3. Keep error logging but remove `DEBUG` prefix from log messages
4. Remove or secure the `KitDocuments_Debug` directory

## Testing Debug Features

A test has been verified that demonstrates all debug features:
1. PDF generation with local storage
2. Email configuration and message logging (with simulated failure)
3. Blob storage configuration logging (with simulated failure)

The test confirms that debug output appears correctly in both console and ILogger output.

## Files Modified

- `BlazorApp/Services/EmailService.cs` - Email debug logging
- `BlazorApp/Services/BlobStorageService.cs` - Blob debug logging  
- `BlazorApp/Services/PdfGenerationService.cs` - PDF debug logging and local storage
- `BlazorApp/Services/FormService.cs` - Orchestration debug logging
- `KitDocuments_Debug/` - Directory for debug PDF files (created automatically)