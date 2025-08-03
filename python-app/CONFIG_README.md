# Development Configuration (config.py)

## ⚠️ IMPORTANT WARNING

**This configuration file is for DEVELOPMENT and DEBUG purposes ONLY!**

The `config.py` file contains hardcoded secrets, passwords, API keys, and connection strings extracted from `BlazorApp/appsettings.json`. This is intended for:

- Local development
- Debugging and testing
- Quick setup without environment variable configuration

**DO NOT use this configuration in production environments!**

## Usage

### Basic Import

```python
import config

# Get specific configuration sections
email_config = config.get_email_config()
storage_config = config.get_blob_storage_config()
app_config = config.get_application_config()
```

### Direct Access

```python
import config

# Access configuration directly
smtp_server = config.EMAIL_SETTINGS['SmtpServer']
database_connection = config.CONNECTION_STRINGS['DefaultConnection']
app_name = config.APPLICATION_SETTINGS['ApplicationName']
```

### All Settings

```python
import config

# Get all settings as a single dictionary (mirrors appsettings.json structure)
all_settings = config.ALL_SETTINGS
```

## Configuration Sections

The configuration includes all sections from `BlazorApp/appsettings.json`:

- **Logging**: Log levels and console configuration
- **ConnectionStrings**: Database connection settings
- **EmailSettings**: SMTP server configuration with credentials
- **BlobStorageSettings**: Azure Storage connection string and container
- **ApplicationSettings**: Application name, URL, and token settings
- **ApplicationInsights**: Telemetry and monitoring configuration
- **Diagnostics**: Retention and diagnostic settings
- **Website**: HTTP logging settings

## Example Usage

```python
#!/usr/bin/env python3
"""
Example: Using hardcoded config for email service
"""
import config

def setup_email_service():
    email_settings = config.EMAIL_SETTINGS
    
    # Configure your email service
    return {
        'host': email_settings['SmtpServer'],
        'port': email_settings['SmtpPort'],
        'username': email_settings['SmtpUsername'],
        'password': email_settings['SmtpPassword'],
        'use_tls': email_settings['UseSsl'],
        'from_address': email_settings['FromEmail']
    }

def setup_storage_service():
    storage_settings = config.BLOB_STORAGE_SETTINGS
    
    # Configure your storage service
    return {
        'connection_string': storage_settings['ConnectionString'],
        'container_name': storage_settings['ContainerName']
    }

if __name__ == "__main__":
    email_config = setup_email_service()
    storage_config = setup_storage_service()
    
    print(f"Email server: {email_config['host']}")
    print(f"Storage container: {storage_config['container_name']}")
```

## Testing

The configuration includes comprehensive tests in `tests/test_hardcoded_config.py`:

```bash
# Run config-specific tests
python -m pytest tests/test_hardcoded_config.py -v

# Test config directly
python config.py

# Run all tests
python -m pytest tests/ -v
```

## Production Usage

For production deployments, continue using the existing environment variable-based configuration system in `app/core/config.py`. The hardcoded config is purely for development convenience.

## Values Included

All values from `BlazorApp/appsettings.json` are included as literal Python values:

- ✅ SMTP credentials (ismailkucukdurgut@gmail.com)
- ✅ Azure Storage connection strings
- ✅ Application Insights instrumentation keys  
- ✅ Database connection strings
- ✅ Application URLs and settings
- ✅ Logging and diagnostic configurations
- ✅ Website and retention settings

Remember: **These are real credentials for development/testing only!**