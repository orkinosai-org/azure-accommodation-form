# Enhanced Development Mode Debugging

This document outlines the comprehensive debugging enhancements made to improve development mode form submission troubleshooting.

## Overview

The Azure Accommodation Form application now includes extensive debugging capabilities specifically designed for development mode. These enhancements provide detailed error logging, request/response analysis, and local storage fallback validation to make development mode submission failures easy to diagnose and fix.

## Key Enhancements

### 1. Server-side Enhanced Error Logging (`FormController.cs`)

#### Request Tracking and Payload Logging
- **Request ID generation**: Each request gets a unique 8-character ID for tracking across logs
- **Development mode detection**: Automatic environment detection for conditional debug output
- **Complete request payload logging**: In development mode, logs the full JSON payload with proper formatting
- **Request metadata logging**: Headers, content type, content length, user agent, and timing

#### Enhanced Exception Handling
- **Complete stack trace logging**: Full exception details including type, source, and stack trace
- **Inner exception traversal**: Recursive logging of all inner exceptions with detailed information
- **Exception data logging**: Additional exception metadata when available
- **Categorized error messages**: Specific error categorization for common failure scenarios:
  - Azure Storage/Azurite connection issues
  - SMTP/Email service failures
  - Database connection problems
  - PDF generation errors
  - File system access issues
  - Network connectivity problems

#### Development Mode Error Responses
- **Technical details in responses**: Development mode includes full technical error details
- **Production safety**: Production mode never exposes sensitive technical information
- **Comprehensive troubleshooting information**: Stack traces, inner exceptions, and diagnostic guidance

#### Enhanced Validation Error Handling
- **Field-level validation analysis**: Detailed breakdown of validation failures with field paths
- **Form structure analysis**: Complete analysis of form data completeness for debugging
- **Development-only detailed validation**: Field values and attempted values logged for debugging
- **Validation error categorization**: Clear categorization of validation failure types

### 2. Client-side Enhanced Debug Output (`FormApiService.cs`)

#### Environment-aware Logging
- **Development mode detection**: Automatic detection of development vs production environment
- **Conditional debug output**: Enhanced logging only in development mode
- **Request tracking**: API call IDs for correlation with server-side logs

#### Comprehensive API Debug Information
- **Request details**: Base address, timeout, headers, payload size and samples
- **Form data completeness analysis**: Section-by-section completeness checking
- **Response analysis**: Headers, status codes, timing, and detailed response parsing
- **Enhanced error categorization**: Improved error message parsing and categorization

#### Network and Connectivity Debugging
- **HTTP exception handling**: Detailed logging of network-related failures
- **Timeout detection**: Task cancellation and timeout identification
- **Response header logging**: Complete response header analysis for debugging

### 3. Local Storage Fallback Enhancement (`BlobStorageService.cs`)

#### Comprehensive Directory and Permission Validation
- **Base directory validation**: System temp directory accessibility checking
- **Permission testing**: Immediate write permission validation after directory creation
- **Disk space checking**: Available disk space validation before file operations
- **File verification**: Post-write file existence and size verification

#### Enhanced Error Handling and Troubleshooting
- **Error categorization**: Specific categorization of file system errors:
  - Permission errors with troubleshooting guidance
  - Directory access issues with system configuration advice
  - I/O errors with disk space and antivirus guidance
  - Path validation with character checking
- **Detailed logging**: Comprehensive logging of directory paths, file sizes, and operations
- **Troubleshooting guidance**: Specific advice for common development environment issues

#### Development Storage Features
- **Local storage fallback**: Automatic fallback to local file system when Azurite unavailable
- **Azurite detection**: Specific detection and guidance for Azure Storage Emulator setup
- **Development URL generation**: Local file:// URLs for development testing

## Usage in Development Mode

### Debugging Form Submission Failures

1. **Check Request Logs**: Look for the unique Request ID in logs to track a specific submission
2. **Review Payload Analysis**: Check form data structure and completeness analysis
3. **Examine Error Categorization**: Review specific error categories for targeted troubleshooting
4. **Local Storage Validation**: Verify local storage fallback is working correctly

### Log Output Examples

#### Request Tracking
```
=== FORM CONTROLLER: DIRECT SUBMISSION ENTRY (Request: a1b2c3d4) ===
Request received at 2024-01-15T10:30:00Z
Environment: Development
Request Content-Type: application/json
DEVELOPMENT ONLY - Request Payload (Request: a1b2c3d4): { ... }
```

#### Error Categorization
```
=== FORM CONTROLLER EXCEPTION (Request: a1b2c3d4) ===
DEVELOPMENT MODE - Full Exception Details:
Exception Type: System.IO.UnauthorizedAccessException
Error Category: Permission Error
Troubleshooting: Ensure the application has write permissions to the temp directory.
```

#### Validation Analysis
```
DEVELOPMENT ONLY - Form data structure analysis (Request: a1b2c3d4):
{
  "TenantDetailsProvided": true,
  "BankDetailsProvided": true,
  "SectionsComplete": 9
}
```

## Testing

The enhanced debugging features include comprehensive testing via `EnhancedDebuggingTest.cs`:

- **Development mode detection testing**
- **Validation error handling verification**
- **Local storage fallback testing**
- **Form data completeness logging validation**

Run tests with: `cd Tests && dotnet run`

## Configuration

No additional configuration is required. The debugging enhancements automatically detect the development environment and activate appropriate logging levels.

### Environment Detection
- Development mode: Full debug output, detailed error messages, request payload logging
- Production mode: Standard logging, user-friendly error messages, no sensitive data exposure

## Security Considerations

- **Production safety**: Technical details are never exposed in production mode
- **Sensitive data protection**: Connection strings and credentials are masked in logs
- **Development-only features**: Enhanced debugging is restricted to development environment

## Troubleshooting Common Issues

### Azure Storage/Azurite Issues
- **Error**: "Connection refused" or "127.0.0.1:10000"
- **Solution**: Start Azurite with `azurite --silent --location c:\azurite --debug c:\azurite\debug.log`

### Local Storage Permission Issues
- **Error**: "Access denied" during local storage fallback
- **Solution**: Check temp directory permissions and antivirus settings

### Email Service Configuration
- **Error**: SMTP connection failures
- **Solution**: Verify email settings in `appsettings.Development.json`

### Database Connection Issues
- **Error**: Entity Framework connection problems
- **Solution**: Verify SQLite database file permissions and disk space

## Summary

These enhancements provide comprehensive debugging capabilities for development mode, making it significantly easier to diagnose and resolve form submission failures. The implementation maintains production security while providing rich debugging information for development environments.