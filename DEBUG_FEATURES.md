# Debug Features for Python Azure Accommodation Form

This document describes the debug features available in the current Python FastAPI implementation.

## Overview

The Python Azure Accommodation Form application includes comprehensive debug logging and monitoring capabilities for:
- Service configuration validation
- Email processing and delivery
- Azure Blob Storage operations  
- PDF generation and processing
- Form submission workflows

## Debug Output Locations

All debug output is available through:
- **Console output**: Real-time application logs with timestamps
- **Application Insights**: Telemetry and performance monitoring (when configured)
- **Local storage**: Fallback file storage for debugging when Azure services are unavailable

## Current Debug Features

### 1. Configuration Auditing
At application startup, a comprehensive configuration audit is performed:
```
=== Configuration Audit ===
Configuration source: appsettings.json file
Environment: development
Email configuration values:
  SMTP Server: smtp.gmail.com
  SMTP Port: 587
  SMTP Username: user@example.com
  SMTP Password: [SET]
  From Email: user@example.com
  Company Email: admin@example.com
  Use SSL: True
=== End Configuration Audit ===
```

### 2. Service-Level Debug Logging

#### Email Service (`app/services/email.py`)
- **Configuration validation**: SMTP settings verification and connection testing
- **Message construction**: Detailed logging of email content, recipients, and attachments
- **Delivery tracking**: Success/failure status with detailed error information
- **Credential protection**: Passwords masked as `[SET]` or `[NOT SET]`

#### Storage Service (`app/services/storage.py`)
- **Azure Blob Storage connectivity**: Connection testing and container verification
- **Upload operations**: File upload progress and completion status
- **Local fallback**: Automatic fallback to local storage with permission validation
- **Error categorization**: Specific error types for storage failures

#### PDF Generation Service (`app/services/pdf.py`)
- **Document creation**: Step-by-step PDF generation process
- **Form data processing**: Template rendering and data transformation
- **File operations**: PDF creation, validation, and storage operations

#### Application Insights Service (`app/services/application_insights.py`)
- **Telemetry initialization**: Service startup and configuration validation
- **Event tracking**: Custom events for application lifecycle and user actions
- **Exception tracking**: Detailed exception logging with stack traces
- **Performance monitoring**: Request timing and dependency tracking

### 3. Environment-Aware Logging

The application automatically detects the environment and adjusts logging accordingly:
- **Development mode**: Enhanced debug output with detailed technical information
- **Production mode**: Structured logging focused on operational monitoring
- **Configuration-based**: Log levels configurable via `appsettings.json`

## Troubleshooting with Debug Features

### Email Issues
1. Check the configuration audit output for SMTP settings
2. Review email service logs for connection and authentication errors
3. Verify recipient addresses and email content formatting

### Storage Issues  
1. Monitor Azure Blob Storage connection status in startup logs
2. Check storage service logs for upload operations and errors
3. Verify local fallback mechanisms when Azure services are unavailable

### Form Processing Issues
1. Review form service logs for validation errors and data processing
2. Check PDF generation logs for template rendering issues
3. Monitor request correlation IDs across services for end-to-end tracking

## Log Message Format

All log messages follow a consistent format:
```
HH:mm:ss service.module - LEVEL - Message with contextual information
```

Examples:
```
10:30:15 app.services.email - INFO - Email sent successfully to user@example.com
10:30:16 app.services.storage - INFO - PDF uploaded to Azure Blob Storage: submission_12345.pdf
10:30:17 app.services.application_insights - INFO - Event tracked: FormSubmissionComplete
```

## Security Considerations

- **Credential protection**: All sensitive information (passwords, connection strings) is masked in logs
- **Personal data**: Form submission data is logged minimally to protect user privacy  
- **Production safety**: Debug information is appropriately filtered in production environments
- **Log rotation**: Application logs are managed to prevent disk space issues

## Monitoring and Alerting

When Application Insights is configured:
- **Real-time monitoring**: Live application performance and error tracking
- **Custom alerts**: Configurable alerts for service failures and performance issues
- **Dashboards**: Visual monitoring of application health and usage patterns
- **Exception tracking**: Automatic exception detection and notification