# Configuration Guide - appsettings.json Configuration

## Overview

The Azure Accommodation Form Python application now uses **ONLY** an `appsettings.json` file for all configuration. Environment variables, `.env` files, and Pydantic BaseSettings are no longer used.

This change provides:
- ✅ Clear, centralized configuration in one file
- ✅ Consistent structure for Python FastAPI applications
- ✅ No dependency on environment variables or `.env` files
- ✅ Fail-fast behavior if configuration is missing or incomplete
- ✅ Better security (no accidental exposure through environment)

## Quick Start

1. **Configuration File Setup:**
   
   The application will automatically detect and copy the most appropriate configuration:
   
   **Option A - Development Setup (Automatic):**
   The application will automatically copy `appsettings.example.json` to `appsettings.json` if no configuration file exists.
   
   **Option B - Manual Setup:**
   ```bash
   # Copy from example template
   cp appsettings.example.json appsettings.json
   ```

2. **Update the EmailSettings section with your SMTP credentials:**
   ```json
   {
     "EmailSettings": {
       "SmtpServer": "smtp.gmail.com",
       "SmtpPort": 587,
       "SmtpUsername": "your-email@gmail.com",
       "SmtpPassword": "your-gmail-app-password",
       "UseSsl": true,
       "FromEmail": "noreply@yourdomain.com",
       "FromName": "Azure Accommodation Form",
       "CompanyEmail": "admin@yourdomain.com"
     }
   }
   ```

3. **Test your configuration:**
   ```bash
   python test_email_config.py your-email@example.com
   ```

## Automatic Configuration Setup

If `appsettings.json` is missing when the application starts, it will:

1. **Check for existing configuration** - Look for `appsettings.json` in the Python app directory
2. **Auto-copy and adapt Blazor config** - If found, copy the production-ready configuration and add Python-specific `ServerSettings`
3. **Fallback to example file (Priority 2)** - If Blazor config not available, check for `appsettings.example.json`
4. **Log informative messages** - Explain which configuration source was used
5. **Fail gracefully** - If no configuration source exists, stop with a clear error message

### Auto-Copy Priority Order:
1. **Configuration File** (`appsettings.json`) - **Primary configuration source**
   - Contains production-ready settings (SMTP, Azure Storage, Application Insights)
   - Automatically adds Python-specific `ServerSettings` section
   - Sets environment to "production"
   - Logs: *"Configuration loaded successfully from appsettings.json"*

2. **Example Configuration** (`appsettings.example.json`) - **Fallback for development**
   - Contains template/example values
   - Requires manual configuration updates
   - Logs: *"Configuration file was missing. Automatically copied from appsettings.example.json"*

This ensures the Python app can start with **template configuration** and requires manual configuration of secrets.

## Configuration Sources and Auto-Detection

The Python app intelligently detects and uses the best available configuration source:

### 1. Configuration File Exists
If `appsettings.json` is already present, the application will use it directly.

### 2. Automatic Template Copy (Fallback)
When no configuration file is available, it will:
- Look for `appsettings.example.json` in the Python app directory
- Copy the example configuration with development defaults
- Require manual updates for SMTP and other service credentials

### 3. Manual Configuration
You can also manually create `appsettings.json` by copying from the example template and customizing as needed.

## Configuration Structure

The `appsettings.json` file uses a structured format optimized for the Python FastAPI application:

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "Microsoft.Hosting.Lifetime": "Information"
    },
    "Console": {
      "IncludeScopes": false,
      "TimestampFormat": "HH:mm:ss "
    }
  },
  "EmailSettings": {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "SmtpUsername": "your-email@gmail.com",
    "SmtpPassword": "your-gmail-app-password",
    "UseSsl": true,
    "FromEmail": "noreply@yourdomain.com",
    "FromName": "Azure Accommodation Form",
    "CompanyEmail": "admin@yourdomain.com"
  },
  "BlobStorageSettings": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=your-key;EndpointSuffix=core.windows.net",
    "ContainerName": "form-submissions"
  },
  "ApplicationSettings": {
    "ApplicationName": "Azure Accommodation Form",
    "ApplicationUrl": "http://localhost:8000",
    "TokenExpirationMinutes": 15,
    "TokenLength": 6
  },
  "ApplicationInsights": {
    "ConnectionString": "InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/",
    "AgentExtensionVersion": "~2",
    "XdtMode": "default"
  },
  "Diagnostics": {
    "AzureBlobRetentionInDays": 2
  },
  "Website": {
    "HttpLoggingRetentionDays": 2
  },
  "ServerSettings": {
    "Environment": "development",
    "SecretKey": "your-secret-key-change-in-production-make-it-long-and-random",
    "Host": "0.0.0.0",
    "Port": 8000,
    "AllowedHosts": ["localhost", "127.0.0.1"],
    "AllowedOrigins": ["http://localhost:8000", "http://127.0.0.1:8000"],
    "SslKeyfile": null,
    "SslCertfile": null
  }
}
```

## Required Email Configuration Fields

The following fields in `EmailSettings` are **required** and the application will fail to start if any are missing:

- `SmtpUsername`: Your SMTP username (email address)
- `SmtpPassword`: Your SMTP password (use app-specific passwords for Gmail)
- `FromEmail`: The "from" email address for outbound emails
- `CompanyEmail`: The company/admin email address for notifications

## Gmail Configuration

For Gmail SMTP, use these settings:

```json
{
  "EmailSettings": {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "SmtpUsername": "your-email@gmail.com",
    "SmtpPassword": "your-app-specific-password",
    "UseSsl": true,
    "FromEmail": "noreply@yourdomain.com",
    "FromName": "Azure Accommodation Form",
    "CompanyEmail": "your-email@gmail.com"
  }
}
```

**Important**: Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular Gmail password.

## Testing Configuration

Use the built-in CLI tool to test your configuration:

```bash
# Test configuration only
python test_email_config.py

# Test configuration and send test email
python test_email_config.py your-email@example.com
```

The tool will:
- ✅ Verify `appsettings.json` exists and is valid JSON
- ✅ Check all required email fields are present
- ✅ Show configuration audit information
- ✅ Optionally send a test email

## Error Handling

### Missing Configuration File
If `appsettings.json` is missing and no configuration source is available:
```
❌ Configuration file 'appsettings.json' not found. 
Unable to find configuration template 'appsettings.example.json'. 
Please create 'appsettings.json' by copying from appsettings.example.json and updating with your values.
```

### Invalid JSON
If `appsettings.json` contains invalid JSON:
```
❌ Invalid JSON in configuration file 'appsettings.json': Expecting ',' delimiter: line 5 column 1 (char 123)
```

### Missing Required Fields
If required email fields are missing:
```
❌ Missing required email configuration fields in appsettings.json: SmtpUsername, SmtpPassword, FromEmail, CompanyEmail. 
Please update your appsettings.json file with the required EmailSettings values.
```

## Migration from Environment Variables

If you previously used environment variables, here's how to migrate:

### Old Environment Variables → New appsettings.json

| Old Environment Variable | New appsettings.json Location |
|---------------------------|---------------------------|
| `EMAIL_SMTP_SERVER` | `EmailSettings.SmtpServer` |
| `EMAIL_SMTP_PORT` | `EmailSettings.SmtpPort` |
| `EMAIL_SMTP_USERNAME` | `EmailSettings.SmtpUsername` |
| `EMAIL_SMTP_PASSWORD` | `EmailSettings.SmtpPassword` |
| `EMAIL_USE_SSL` | `EmailSettings.UseSsl` |
| `EMAIL_FROM_EMAIL` | `EmailSettings.FromEmail` |
| `EMAIL_FROM_NAME` | `EmailSettings.FromName` |
| `EMAIL_COMPANY_EMAIL` | `EmailSettings.CompanyEmail` |
| `APPLICATION_NAME` | `ApplicationSettings.ApplicationName` |
| `APPLICATION_URL` | `ApplicationSettings.ApplicationUrl` |
| `ENVIRONMENT` | `ServerSettings.Environment` |
| `PORT` | `ServerSettings.Port` |

**Important**: Environment variables are now completely ignored. Only `appsettings.json` values are used.

## Security Considerations

1. **Never commit `appsettings.json` to version control** if it contains sensitive information
2. Use `appsettings.example.json` as a template with placeholder values
3. Set appropriate file permissions on `appsettings.json` (e.g., `600`)
4. For production, consider using Azure Key Vault or similar secure storage

## Deployment

### Development
1. Copy `appsettings.example.json` to `appsettings.json`
2. Update with your development SMTP credentials
3. Run the application

### Production
1. Create `appsettings.json` with production values
2. Ensure secure file permissions
3. Update `ServerSettings.Environment` to `"production"`
4. Use strong `ServerSettings.SecretKey`

## Troubleshooting

### Application Won't Start
Check the error message:
- Missing `appsettings.json` file → Will auto-copy from Blazor app or example file
- No configuration sources → Copy from `appsettings.example.json`
- Invalid JSON → Validate JSON syntax
- Missing fields → Add required EmailSettings fields

### Email Not Sending
Run the configuration test:
```bash
python test_email_config.py your-email@example.com
```

Common issues:
- Incorrect SMTP credentials
- Gmail requires app-specific password
- Firewall blocking SMTP port 587
- `UseSsl` setting incorrect for your SMTP server

### Configuration Audit
The application logs detailed configuration information at startup:
```
INFO:app.core.config:=== Configuration Audit ===
INFO:app.core.config:Configuration source: appsettings.json file
INFO:app.core.config:Environment: development
INFO:app.core.config:Email configuration values:
INFO:app.core.config:  SMTP Server: smtp.gmail.com
INFO:app.core.config:  SMTP Port: 587
INFO:app.core.config:  SMTP Username: your-email@gmail.com
INFO:app.core.config:  SMTP Password: [SET]
```

## Changes Made

This refactoring involved:

1. **Removed dependencies:**
   - `python-dotenv` (no longer needed)
   - `pydantic-settings` (replaced with dataclasses)
   - Environment variable loading logic

2. **Added JSON-based configuration:**
   - `load_config_from_file()` function
   - `create_settings_from_config()` function
   - Dataclass-based configuration structures

3. **Enhanced error handling:**
   - Clear error messages for missing files
   - Validation of required email fields
   - JSON parsing error handling

4. **Updated tools:**
   - `test_email_config.py` CLI tool
   - Comprehensive test suite
   - Configuration audit logging

The application now loads configuration ONLY from `appsettings.json` and will fail fast with clear error messages if the configuration is incomplete or missing.