# Azure Accommodation Form - Python Configuration Guide

This document explains how to configure the Python web application to use all settings from the .NET Blazor application's `appsettings.json` file.

## Overview

The Python application now mirrors the complete configuration structure from the .NET Blazor application, providing Python equivalents for all settings including:

- **Logging Configuration** - Log levels and console formatting
- **Email/SMTP Settings** - Complete email service configuration
- **Azure Blob Storage** - File storage configuration
- **Application Settings** - Application metadata and token configuration
- **Application Insights** - Telemetry and monitoring
- **Diagnostics** - Retention policies and logging settings

## Configuration Structure

### 1. Logging Configuration

Maps .NET logging levels to Python logging levels:

| .NET Level | Python Level | Description |
|------------|--------------|-------------|
| Trace | DEBUG | Detailed debugging information |
| Debug | DEBUG | General debugging information |
| Information | INFO | General information messages |
| Warning | WARNING | Warning messages |
| Error | ERROR | Error messages |
| Critical | CRITICAL | Critical error messages |

**Environment Variables:**
```bash
# Log levels (TRACE, DEBUG, INFORMATION, WARNING, ERROR, CRITICAL)
LOGGING_DEFAULT_LEVEL=INFORMATION
LOGGING_MICROSOFT_LEVEL=WARNING
LOGGING_MICROSOFT_HOSTING_LIFETIME_LEVEL=INFORMATION

# Console formatting
LOGGING_CONSOLE_INCLUDE_SCOPES=false
LOGGING_CONSOLE_TIMESTAMP_FORMAT="HH:mm:ss "
```

**Usage in Code:**
```python
from app.core.config import get_settings
import logging.config

settings = get_settings()
logging_config = settings.get_logging_config()
logging.config.dictConfig(logging_config)
```

### 2. Email Settings

Complete SMTP configuration that mirrors .NET `EmailSettings`:

**Environment Variables:**
```bash
# Primary email configuration (new format)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_USE_SSL=true
EMAIL_FROM_EMAIL=noreply@yourdomain.com
EMAIL_FROM_NAME=Azure Accommodation Form
EMAIL_COMPANY_EMAIL=admin@yourdomain.com

# Legacy environment variables (for backward compatibility)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Azure Accommodation Form
ADMIN_EMAIL=admin@yourdomain.com
```

**Usage in Code:**
```python
from app.core.config import get_settings
from app.services.email import EmailService

settings = get_settings()
email_service = EmailService()

# Send email using configured SMTP settings
await email_service.send_mfa_token("user@example.com", "123456")
```

### 3. Azure Blob Storage Settings

Mirrors .NET `BlobStorageSettings`:

**Environment Variables:**
```bash
# Primary blob storage configuration (new format)
BLOB_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
BLOB_STORAGE_CONTAINER_NAME=form-submissions

# Legacy environment variables (for backward compatibility)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=form-submissions
```

**Usage in Code:**
```python
from app.services.storage import AzureBlobStorageService

storage_service = AzureBlobStorageService()
await storage_service.upload_file("filename.pdf", file_content)
```

### 4. Application Settings

Mirrors .NET `ApplicationSettings`:

**Environment Variables:**
```bash
# Primary application configuration (new format)
APPLICATION_APPLICATION_NAME=Azure Accommodation Form
APPLICATION_APPLICATION_URL=http://localhost:8000
APPLICATION_TOKEN_EXPIRATION_MINUTES=15
APPLICATION_TOKEN_LENGTH=6

# Legacy environment variables (for backward compatibility)
APPLICATION_NAME=Azure Accommodation Form
APPLICATION_URL=http://localhost:8000
TOKEN_EXPIRATION_MINUTES=15
TOKEN_LENGTH=6
```

**Usage in Code:**
```python
from app.core.config import get_settings

settings = get_settings()
app_name = settings.application_settings.application_name
token_length = settings.application_settings.token_length
```

### 5. Application Insights

Mirrors .NET `ApplicationInsights` configuration:

**Environment Variables:**
```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/
APPLICATIONINSIGHTS_AGENT_VERSION=~2
APPLICATIONINSIGHTS_XDT_MODE=default
```

**Usage in Code:**
```python
from app.services.application_insights import get_insights_service

insights = get_insights_service()

# Track events (similar to .NET TrackEvent)
insights.track_event("UserLogin", {"user_id": "123", "source": "web"})

# Track exceptions (similar to .NET TrackException)
try:
    # some operation
    pass
except Exception as e:
    insights.track_exception(e, {"operation": "user_registration"})

# Track dependencies (similar to .NET TrackDependency)
insights.track_dependency("Azure Storage", "upload_file", 150.0, True)

# Track requests (similar to .NET TrackRequest)
insights.track_request("POST /api/form", "/api/form/submit", 200.0, 200, True)
```

### 6. Diagnostics Settings

Mirrors .NET `Diagnostics` and `Website` configuration:

**Environment Variables:**
```bash
DIAGNOSTICS_BLOB_RETENTION_DAYS=2
DIAGNOSTICS_HTTP_RETENTION_DAYS=2
```

**Usage in Code:**
```python
from app.core.config import get_settings

settings = get_settings()
blob_retention = settings.diagnostics.azure_blob_retention_days
http_retention = settings.diagnostics.http_logging_retention_days
```

## Setting Up Configuration

### 1. Create Environment File

Copy the example environment file and customize it:

```bash
cd python-app
cp .env.example .env
# Edit .env with your actual configuration values
```

### 2. Configure Email Service

For Gmail SMTP (recommended for development):

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the App Password as `EMAIL_SMTP_PASSWORD`

Example configuration:
```bash
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=youremail@gmail.com
EMAIL_SMTP_PASSWORD=your-16-character-app-password
EMAIL_USE_SSL=true
EMAIL_FROM_EMAIL=noreply@yourdomain.com
EMAIL_FROM_NAME=Azure Accommodation Form
EMAIL_COMPANY_EMAIL=admin@yourdomain.com
```

### 3. Configure Azure Blob Storage

1. Create an Azure Storage Account
2. Get the connection string from Azure Portal → Storage Account → Access keys
3. Create a container named `form-submissions` (or customize the name)

Example configuration:
```bash
BLOB_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=youraccountkey;EndpointSuffix=core.windows.net
BLOB_STORAGE_CONTAINER_NAME=form-submissions
```

### 4. Configure Application Insights

1. Create an Application Insights resource in Azure
2. Get the connection string from Azure Portal → Application Insights → Overview
3. Configure the connection string

Example configuration:
```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://ukwest-0.in.applicationinsights.azure.com/;LiveEndpoint=https://ukwest.livediagnostics.monitor.azure.com/
```

## Security Best Practices

### 1. Environment Variables for Secrets

Never commit sensitive information to source control. Always use environment variables:

- `EMAIL_SMTP_PASSWORD` - Email service password
- `BLOB_STORAGE_CONNECTION_STRING` - Azure Storage connection string
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - Application Insights connection string
- `SECRET_KEY` - Application secret key

### 2. Production Configuration

For production deployment:

```bash
ENVIRONMENT=production
SECRET_KEY=very-long-random-secret-key-for-production-use
# Set all other production values
```

### 3. Azure Key Vault Integration

For enhanced security in production, consider integrating with Azure Key Vault:

```python
# Example: Load secrets from Azure Key Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def load_from_key_vault():
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
    
    return {
        "EMAIL_SMTP_PASSWORD": client.get_secret("email-smtp-password").value,
        "BLOB_STORAGE_CONNECTION_STRING": client.get_secret("blob-storage-connection").value,
        # ... other secrets
    }
```

## Migration from .NET appsettings.json

### Mapping .NET to Python Configuration

| .NET Section | Python Equivalent | Environment Prefix |
|--------------|-------------------|-------------------|
| `Logging.LogLevel` | `LoggingSettings` | `LOGGING_` |
| `EmailSettings` | `EmailSettings` | `EMAIL_` |
| `BlobStorageSettings` | `BlobStorageSettings` | `BLOB_STORAGE_` |
| `ApplicationSettings` | `ApplicationSettings` | `APPLICATION_` |
| `ApplicationInsights` | `ApplicationInsightsSettings` | `APPLICATIONINSIGHTS_` |
| `Diagnostics` | `DiagnosticsSettings` | `DIAGNOSTICS_` |

### Settings Not Implemented

The following .NET settings are intentionally not implemented as they're handled differently in Python/FastAPI:

- `AllowedHosts` - Handled by FastAPI middleware
- `ConnectionStrings.DefaultConnection` - No database used in current implementation

### Backward Compatibility

The application maintains backward compatibility with existing environment variable names:

- `SMTP_*` variables still work alongside `EMAIL_*` variables
- `AZURE_STORAGE_*` variables still work alongside `BLOB_STORAGE_*` variables
- `MFA_TOKEN_*` variables are mapped to `APPLICATION_TOKEN_*` settings

## Testing Configuration

Run the configuration tests to verify your setup:

```bash
cd python-app
python -m pytest tests/test_config.py -v
```

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check SMTP credentials and App Password
   - Verify firewall allows SMTP traffic on port 587
   - Check Gmail security settings

2. **Azure Blob Storage connection failed**
   - Verify connection string format
   - Check storage account access keys
   - Ensure container exists

3. **Application Insights not working**
   - Verify connection string format
   - Check Azure Application Insights resource status
   - Install optional dependencies: `pip install opencensus-ext-azure`

4. **Configuration not loading**
   - Check `.env` file is in the correct location
   - Verify environment variable names match exactly
   - Clear cache: `get_settings.cache_clear()` in development

### Debug Configuration

The application now includes comprehensive configuration auditing and debugging features.

#### Automatic Configuration Audit at Startup

When the application starts, it automatically performs a configuration audit and logs:

- Which configuration sources are available (.env file, environment variables)
- How many email configuration variables are set (new vs. legacy format)
- Current email configuration values (excluding secrets)
- Missing required fields with specific guidance
- Configuration warnings

Example startup log output:
```
INFO: === Configuration Audit ===
INFO: Environment file (.env): Found
INFO: Environment: development
INFO: Email configuration sources:
INFO:   New format (EMAIL_*): 6/6 variables set
INFO:   Legacy format (SMTP_*, FROM_*, ADMIN_*): 0/6 variables set
INFO: Email configuration values:
INFO:   SMTP Server: smtp.gmail.com
INFO:   SMTP Port: 587
INFO:   SMTP Username: test@example.com
INFO:   SMTP Password: [SET]
INFO:   From Email: noreply@example.com
INFO:   From Name: Azure Accommodation Form
INFO:   Company Email: admin@example.com
INFO: === End Configuration Audit ===
```

#### CLI Configuration Testing Tool

Use the included CLI tool to test email configuration:

```bash
# Test configuration only
python test_email_config.py

# Test configuration and send test email
python test_email_config.py your-email@example.com
```

The CLI tool provides:
- Complete configuration audit
- Clear indication of missing fields
- Specific guidance on how to set missing variables
- Test email sending capability
- Detailed error reporting

#### API Endpoints for Configuration Testing

##### Public Configuration Status Endpoint

```bash
curl http://localhost:8000/config-status
```

Returns basic configuration status (excludes secrets):
```json
{
    "status": "ok",
    "environment": "development",
    "email_service": {
        "configured": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    },
    "storage_service": {
        "configured": false
    },
    "application_insights": {
        "configured": false
    }
}
```

##### Admin Email Configuration Endpoint

Requires admin authentication (`X-Admin-Token` header):

```bash
curl -H "X-Admin-Token: your-admin-token" \
     http://localhost:8000/api/admin/config/email
```

Returns detailed email configuration audit:
```json
{
    "email_config": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": "test@example.com",
        "smtp_password": "[SET]",
        "use_ssl": true,
        "from_email": "noreply@example.com",
        "from_name": "Azure Accommodation Form",
        "company_email": "admin@example.com"
    },
    "config_audit": {
        "config_sources": {
            "env_file": true,
            "environment_vars": true
        },
        "email_config": {
            "new_format_vars": {
                "EMAIL_SMTP_SERVER": true,
                "EMAIL_SMTP_USERNAME": true,
                // ... other variables
            },
            "legacy_format_vars": {
                "SMTP_SERVER": false,
                "SMTP_USERNAME": false,
                // ... other variables
            }
        },
        "missing_fields": [],
        "warnings": []
    },
    "ready_for_email": true
}
```

##### Admin Test Email Endpoint

Send a test email (requires admin authentication):

```bash
curl -X POST \
     -H "X-Admin-Token: your-admin-token" \
     -H "Content-Type: application/json" \
     -d '{"to_email": "test@example.com", "message": "Custom test message"}' \
     http://localhost:8000/api/admin/config/email/test
```

#### Configuration Loading with Fallback Logic

The email configuration system now includes intelligent fallback logic:

1. **Primary**: Load from EMAIL_ prefixed environment variables
2. **Fallback**: Load from legacy SMTP_*, FROM_*, ADMIN_* variables if EMAIL_ variables are not set
3. **Guidance**: Provide specific error messages for missing fields

This ensures backward compatibility while encouraging migration to the new format.

#### Debugging Missing Configuration

When email configuration is incomplete, the system provides specific guidance:

```
WARNING: Missing required email field: smtp_username
WARNING:   Set environment variable: EMAIL_SMTP_USERNAME or SMTP_USERNAME
WARNING:   Example value: your-email@gmail.com
```

#### Programmatic Configuration Testing

For custom debugging, use the configuration audit method:

```python
from app.core.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
settings = get_settings()

# Perform configuration audit
audit_info = settings.audit_configuration()

# Check specific issues
email_ready = bool(
    settings.email_settings.smtp_username and 
    settings.email_settings.smtp_password
)

print(f"Email ready: {email_ready}")
print(f"Missing fields: {len(audit_info.get('missing_fields', []))}")
print(f"Warnings: {len(audit_info.get('warnings', []))}")
```

## Additional Resources

- [FastAPI Configuration Documentation](https://fastapi.tiangolo.com/advanced/settings/)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/usage/settings/)
- [Azure Storage Python SDK](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python)
- [Azure Application Insights Python](https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python)