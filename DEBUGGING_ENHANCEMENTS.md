# Python Application Debugging Features

This document outlines the debugging and logging capabilities of the current Python FastAPI implementation.

## Overview

The Azure Accommodation Form application is built with Python FastAPI and includes comprehensive logging and debugging capabilities for development and production environments.

## Current Debugging Features

### 1. Application Insights Integration
- **Telemetry tracking**: Automatic event, exception, and dependency tracking via `app/services/application_insights.py`
- **Custom properties**: Environment-specific metadata and correlation IDs
- **Performance monitoring**: Request timing and application performance metrics
- **Exception tracking**: Detailed exception logging with stack traces

### 2. Comprehensive Logging System
- **Structured logging**: JSON-formatted logs with consistent structure throughout the application
- **Environment-aware logging**: Different log levels for development vs production
- **Service-specific logging**: Dedicated loggers for each service (email, storage, pdf, form processing)
- **Request correlation**: Unique request IDs for tracking across services
- **Configuration auditing**: Complete startup configuration validation with masked secrets

### 3. Service-Level Debugging

#### Email Service (`app/services/email.py`)
- **SMTP configuration validation**: Comprehensive connection testing and validation
- **Message construction logging**: Detailed logging of email content and attachments
- **Error categorization**: Specific error handling for SMTP failures and configuration issues

#### Storage Service (`app/services/storage.py`)
- **Azure Blob Storage monitoring**: Connection status and operation logging
- **Local fallback debugging**: Comprehensive local storage fallback with permission validation
- **File operation tracking**: Detailed logging of upload operations and file handling

#### PDF Generation Service (`app/services/pdf.py`)
- **Document generation logging**: Step-by-step PDF creation process logging
- **Template processing**: Form data processing and template rendering debugging
- **Error handling**: Detailed error reporting for PDF generation failures

#### Form Processing Service (`app/services/form.py`)
- **Request processing**: Complete form submission workflow logging
- **Validation debugging**: Detailed field-level validation error reporting
- **Data transformation**: Logging of form data processing and transformation steps

### 4. Development Environment Features
- **Real-time configuration audit**: Startup configuration validation with clear status reporting
- **Service connectivity verification**: Automatic testing of all external service connections
- **Enhanced error responses**: Detailed error information in development mode
- **Debug output formatting**: Timestamped, categorized log output for easy debugging

## Accessing Debug Information

### Console Output
All debug information is available in the application console with timestamped, categorized output:
```
HH:mm:ss main - INFO - Starting Azure Accommodation Form application...
HH:mm:ss main - INFO - === Configuration Audit ===
HH:mm:ss app.services.storage - INFO - Azure Blob Storage initialized
```

### Application Insights
When configured, detailed telemetry is sent to Azure Application Insights including:
- Custom events for application lifecycle
- Exception tracking with full context
- Dependency tracking for external services
- Performance counters and metrics

### Log Levels
The application supports configurable log levels in `appsettings.json`:
- **Debug**: Detailed technical information
- **Info**: General application flow information  
- **Warning**: Potentially harmful situations
- **Error**: Error events that allow the application to continue
- **Critical**: Serious error events that may cause termination

## Troubleshooting Common Issues

### Form Submission Failures
1. Check the main application logs for request processing errors
2. Verify email service configuration in the startup audit
3. Confirm Azure Storage connectivity status
4. Review PDF generation logs for template processing issues

### Service Configuration Issues
1. Review the configuration audit output at application startup
2. Check service-specific error messages in the logs
3. Verify Azure service credentials and connection strings
4. Confirm local fallback mechanisms are working correctly

## Security Considerations
- **Credential masking**: All passwords and secrets are masked in logs as `[SET]` or `[NOT SET]`
- **Personal data protection**: Form submission data is logged minimally to protect privacy
- **Production safety**: Enhanced debug information is only available in development mode