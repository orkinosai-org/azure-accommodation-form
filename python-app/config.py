"""
Development/Debug Configuration File

⚠️ WARNING: This configuration file is for DEVELOPMENT and DEBUG purposes ONLY!
DO NOT use this file in production environments.

This file contains hardcoded values extracted from BlazorApp/appsettings.json
for convenient development and debugging. All secrets, passwords, and API keys
are present as literal values for non-production use only.

For production deployments, use environment variables or secure configuration
management systems instead.
"""

# Logging Configuration (mirrors BlazorApp/appsettings.json Logging section)
LOGGING = {
    "LogLevel": {
        "Default": "Information",
        "Microsoft": "Warning",
        "Microsoft.Hosting.Lifetime": "Information"
    },
    "Console": {
        "IncludeScopes": False,
        "TimestampFormat": "HH:mm:ss "
    }
}

# Allowed Hosts (mirrors BlazorApp/appsettings.json AllowedHosts)
ALLOWED_HOSTS = "*"

# Connection Strings (mirrors BlazorApp/appsettings.json ConnectionStrings section)
CONNECTION_STRINGS = {
    "DefaultConnection": "Data Source=FormSubmissions.db"
}

# Email Settings (mirrors BlazorApp/appsettings.json EmailSettings section)
# ⚠️ Contains real email credentials for dev/debug only
EMAIL_SETTINGS = {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "SmtpUsername": "ismailkucukdurgut@gmail.com",
    "SmtpPassword": "ftin cwaw jiii fwar",
    "UseSsl": True,
    "FromEmail": "noreply@gmail.com",
    "FromName": "Azure Accommodation Form",
    "CompanyEmail": "ismailkucukdurgut@gmail.com"
}

# Blob Storage Settings (mirrors BlazorApp/appsettings.json BlobStorageSettings section)
# ⚠️ Contains real Azure Storage credentials for dev/debug only
BLOB_STORAGE_SETTINGS = {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=accofornstorageaccount;AccountKey=MTJf54NM7TEcpGTVRaokyTU+6Uy08H8OubuMOrwOhAy2K3hbNbQLvKpyHI/Iq/0p28NnJwtn/gTv+AStsL0GEg==;EndpointSuffix=core.windows.net",
    "ContainerName": "form-submissions"
}

# Application Settings (mirrors BlazorApp/appsettings.json ApplicationSettings section)
APPLICATION_SETTINGS = {
    "ApplicationName": "Azure Accommodation Form",
    "ApplicationUrl": "https://aform-ebb5hjh4dsdgb4gu.ukwest-01.azurewebsites.net/",
    "TokenExpirationMinutes": 15,
    "TokenLength": 6
}

# Application Insights (mirrors BlazorApp/appsettings.json ApplicationInsights section)
# ⚠️ Contains real Application Insights credentials for dev/debug only
APPLICATION_INSIGHTS = {
    "ConnectionString": "InstrumentationKey=a8cb780f-699d-4342-8885-7d5acd08835d;IngestionEndpoint=https://ukwest-0.in.applicationinsights.azure.com/;LiveEndpoint=https://ukwest.livediagnostics.monitor.azure.com/;ApplicationId=0ac0fdf1-4c84-4a6c-9bc9-d624bc121836",
    "AgentExtensionVersion": "~2",
    "XDT_Mode": "default"
}

# Diagnostics Settings (mirrors BlazorApp/appsettings.json Diagnostics section)
DIAGNOSTICS = {
    "AzureBlobRetentionInDays": 2
}

# Website Settings (mirrors BlazorApp/appsettings.json Website section)
WEBSITE = {
    "HttpLoggingRetentionDays": 2
}

# Convenience functions for accessing configuration values
def get_email_config():
    """Get email configuration as a simple dictionary"""
    return EMAIL_SETTINGS.copy()

def get_blob_storage_config():
    """Get blob storage configuration as a simple dictionary"""
    return BLOB_STORAGE_SETTINGS.copy()

def get_application_insights_config():
    """Get Application Insights configuration as a simple dictionary"""
    return APPLICATION_INSIGHTS.copy()

def get_application_config():
    """Get application settings as a simple dictionary"""
    return APPLICATION_SETTINGS.copy()

def get_logging_config():
    """Get logging configuration as a simple dictionary"""
    return LOGGING.copy()

def get_database_connection_string():
    """Get the default database connection string"""
    return CONNECTION_STRINGS["DefaultConnection"]

# All settings combined in a single dictionary for easy access
ALL_SETTINGS = {
    "Logging": LOGGING,
    "AllowedHosts": ALLOWED_HOSTS,
    "ConnectionStrings": CONNECTION_STRINGS,
    "EmailSettings": EMAIL_SETTINGS,
    "BlobStorageSettings": BLOB_STORAGE_SETTINGS,
    "ApplicationSettings": APPLICATION_SETTINGS,
    "ApplicationInsights": APPLICATION_INSIGHTS,
    "Diagnostics": DIAGNOSTICS,
    "Website": WEBSITE
}

# Environment indicator
ENVIRONMENT = "development"
DEBUG = True

if __name__ == "__main__":
    print("🚨 DEVELOPMENT/DEBUG CONFIGURATION LOADED 🚨")
    print("This configuration contains hardcoded secrets and should NEVER be used in production!")
    print(f"Application: {APPLICATION_SETTINGS['ApplicationName']}")
    print(f"Email Server: {EMAIL_SETTINGS['SmtpServer']}")
    print(f"Storage Account: accofornstorageaccount")
    print(f"Database: {CONNECTION_STRINGS['DefaultConnection']}")