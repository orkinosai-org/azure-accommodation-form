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
- **Browser console** (via JavaScript interop for real-time debugging)
- **Local PDF files** (saved in `KitDocuments_Debug` directory)

## New: Browser Console Integration

A new `DebugConsoleHelper` service has been implemented that uses JavaScript interop to send debug logs directly to the browser console. This provides real-time visibility of debug information during form submissions and API calls.

### DebugConsoleHelper Features
- **LogAsync()** - Send general debug messages to browser console
- **LogInfoAsync()** - Send info-level messages (blue in most browsers)
- **LogWarningAsync()** - Send warning messages (yellow in most browsers)  
- **LogErrorAsync()** - Send error messages (red in most browsers)
- **LogGroupAsync()** - Start a collapsible group in browser console
- **LogGroupEndAsync()** - End a console group

All browser console messages are prefixed with `[DEBUG timestamp]` for easy identification.

### JavaScript Integration
The debug console functionality is powered by `wwwroot/js/debug-console.js` which provides the browser-side implementation.

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

**Browser Console Integration:**
- Email configuration grouped in browser console
- Message details with grouped logging
- Real-time send status updates

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

**Browser Console Integration:**
- Blob storage configuration grouped in browser console
- Upload progress and results in real-time

### 3. PdfGenerationService (`BlazorApp/Services/PdfGenerationService.cs`)

**Generation Logging:**
- Submission details (ID, timestamp, client IP)
- Tenant information
- PDF file size

**Local Debug Storage:**
- Saves PDF copy to `KitDocuments_Debug/[SubmissionId]_[Timestamp]_debug.pdf`
- Creates directory automatically if it doesn't exist

**Browser Console Integration:**
- PDF generation progress grouped in browser console
- Local file save confirmation

### 4. FormService (`BlazorApp/Services/FormService.cs`)

**Orchestration Logging:**
- Clear phase markers for PDF generation, blob upload, and email sending
- Submission tracking throughout the process

**Browser Console Integration:**
- Form submission workflow phases logged to browser console
- Step-by-step progress updates in real-time

### 5. DebugConsoleHelper (`BlazorApp/Services/DebugConsoleHelper.cs`) - NEW

**Browser Console Integration:**
- JavaScript interop for real-time browser console logging
- Grouped logging for better organization
- Different log levels (info, warning, error)
- Automatic timestamping of all messages
- Fallback to server-side logging if JS interop fails

## Example Debug Output

### Server Console Output
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

### Browser Console Output
All the above information is also sent to the browser console with organized grouping:

```javascript
[DEBUG 2024-01-15T10:30:00.000Z] PDF GENERATION DEBUG
  [DEBUG 2024-01-15T10:30:00.001Z] Submission ID: test-submission-123  
  [DEBUG 2024-01-15T10:30:00.002Z] Submission Time: 2024-01-15 10:30:00 UTC
  [DEBUG 2024-01-15T10:30:00.003Z] Client IP: 192.168.1.100
  [DEBUG 2024-01-15T10:30:00.004Z] Tenant Name: John Doe
  [DEBUG 2024-01-15T10:30:00.005Z] Tenant Email: john@example.com

[DEBUG 2024-01-15T10:30:01.000Z] EMAIL DEBUG INFO  
  [DEBUG 2024-01-15T10:30:01.001Z] SMTP Server: smtp.gmail.com
  [DEBUG 2024-01-15T10:30:01.002Z] SMTP Port: 587
  [DEBUG 2024-01-15T10:30:01.003Z] Use SSL: True
  [DEBUG 2024-01-15T10:30:01.004Z] Username: noreply@company.com
  [DEBUG 2024-01-15T10:30:01.005Z] Password: ***CONFIGURED***
  // ... additional grouped output
```

## Security Considerations

- **Passwords are masked** in all output as `***CONFIGURED***` or `***NOT SET***`
- **Connection string secrets are masked** using regex patterns
- **Personal data** in form submissions may appear in debug logs - review before sharing logs

## Removing Debug Code for Production

All debug code is marked with comments for easy removal:

```csharp
// DEBUG: Log configuration to browser console (production: remove this section)
await _debugConsole.LogGroupAsync("EMAIL DEBUG INFO");
await _debugConsole.LogAsync($"SMTP Server: {_emailSettings.SmtpServer}");
// ... debug code here ...

// DEBUG: Enhanced error logging (production: keep but remove DEBUG prefix)
```

To prepare for production:
1. Search for `// DEBUG:` comments
2. Remove sections marked `(production: remove this section)`
3. Keep error logging but remove `DEBUG` prefix from log messages
4. Remove or secure the `KitDocuments_Debug` directory
5. Remove the debug console JavaScript file: `wwwroot/js/debug-console.js`
6. Remove the script reference from `Components/App.razor`
7. Remove `IDebugConsoleHelper` service registration from `Program.cs`

## Testing Debug Features

Tests have been verified that demonstrate all debug features:
1. PDF generation with local storage and browser console logging
2. Email configuration and message logging (with simulated failure)
3. Blob storage configuration logging (with simulated failure)
4. Browser console integration via JavaScript interop

The tests confirm that debug output appears correctly in server console, ILogger output, and browser console.

## Files Modified/Added

### New Files
- `BlazorApp/Services/DebugConsoleHelper.cs` - Browser console helper service
- `BlazorApp/wwwroot/js/debug-console.js` - JavaScript interop functions
- `Tests/DebugConsoleHelperTest.cs` - Test for browser console functionality

### Modified Files
- `BlazorApp/Services/EmailService.cs` - Email debug logging + browser console
- `BlazorApp/Services/BlobStorageService.cs` - Blob debug logging + browser console  
- `BlazorApp/Services/PdfGenerationService.cs` - PDF debug logging + browser console
- `BlazorApp/Services/FormService.cs` - Orchestration debug logging + browser console
- `BlazorApp/Program.cs` - Register DebugConsoleHelper service
- `BlazorApp/Components/App.razor` - Include debug console JavaScript file
- `KitDocuments_Debug/` - Directory for debug PDF files (created automatically)