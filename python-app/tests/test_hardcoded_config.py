"""
Test for the hardcoded development configuration file
"""

import sys
import os

# Add the python-app directory to the path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


def test_config_imports_successfully():
    """Test that the config module can be imported without errors"""
    assert config is not None


def test_email_settings_structure():
    """Test that email settings have the correct structure and values"""
    email_config = config.get_email_config()
    
    assert email_config["SmtpServer"] == "smtp.gmail.com"
    assert email_config["SmtpPort"] == 587
    assert email_config["SmtpUsername"] == "ismailkucukdurgut@gmail.com"
    assert email_config["SmtpPassword"] == "ftin cwaw jiii fwar"
    assert email_config["UseSsl"] is True
    assert email_config["FromEmail"] == "noreply@gmail.com"
    assert email_config["FromName"] == "Azure Accommodation Form"
    assert email_config["CompanyEmail"] == "ismailkucukdurgut@gmail.com"


def test_blob_storage_settings_structure():
    """Test that blob storage settings have the correct structure and values"""
    blob_config = config.get_blob_storage_config()
    
    assert "accofornstorageaccount" in blob_config["ConnectionString"]
    assert blob_config["ContainerName"] == "form-submissions"


def test_application_settings_structure():
    """Test that application settings have the correct structure and values"""
    app_config = config.get_application_config()
    
    assert app_config["ApplicationName"] == "Azure Accommodation Form"
    assert app_config["ApplicationUrl"] == "https://aform-ebb5hjh4dsdgb4gu.ukwest-01.azurewebsites.net/"
    assert app_config["TokenExpirationMinutes"] == 15
    assert app_config["TokenLength"] == 6


def test_application_insights_settings():
    """Test that Application Insights settings have the correct structure"""
    insights_config = config.get_application_insights_config()
    
    assert "InstrumentationKey=a8cb780f-699d-4342-8885-7d5acd08835d" in insights_config["ConnectionString"]
    assert insights_config["AgentExtensionVersion"] == "~2"
    assert insights_config["XDT_Mode"] == "default"


def test_logging_settings_structure():
    """Test that logging settings have the correct structure"""
    logging_config = config.get_logging_config()
    
    assert logging_config["LogLevel"]["Default"] == "Information"
    assert logging_config["LogLevel"]["Microsoft"] == "Warning"
    assert logging_config["LogLevel"]["Microsoft.Hosting.Lifetime"] == "Information"
    assert logging_config["Console"]["IncludeScopes"] is False
    assert logging_config["Console"]["TimestampFormat"] == "HH:mm:ss "


def test_database_connection_string():
    """Test that database connection string is correct"""
    db_conn = config.get_database_connection_string()
    assert db_conn == "Data Source=FormSubmissions.db"


def test_diagnostics_and_website_settings():
    """Test that diagnostics and website settings are correct"""
    assert config.DIAGNOSTICS["AzureBlobRetentionInDays"] == 2
    assert config.WEBSITE["HttpLoggingRetentionDays"] == 2


def test_environment_settings():
    """Test that environment settings indicate development mode"""
    assert config.ENVIRONMENT == "development"
    assert config.DEBUG is True


def test_all_settings_structure():
    """Test that the combined ALL_SETTINGS dictionary contains all sections"""
    all_settings = config.ALL_SETTINGS
    
    required_sections = [
        "Logging", "AllowedHosts", "ConnectionStrings", "EmailSettings",
        "BlobStorageSettings", "ApplicationSettings", "ApplicationInsights",
        "Diagnostics", "Website"
    ]
    
    for section in required_sections:
        assert section in all_settings, f"Missing section: {section}"


def test_hardcoded_values_match_appsettings():
    """Test that hardcoded values match what's expected from appsettings.json"""
    # Test specific critical values that should match appsettings.json exactly
    assert config.EMAIL_SETTINGS["SmtpUsername"] == "ismailkucukdurgut@gmail.com"
    assert config.EMAIL_SETTINGS["CompanyEmail"] == "ismailkucukdurgut@gmail.com"
    assert config.APPLICATION_SETTINGS["ApplicationUrl"] == "https://aform-ebb5hjh4dsdgb4gu.ukwest-01.azurewebsites.net/"
    assert config.CONNECTION_STRINGS["DefaultConnection"] == "Data Source=FormSubmissions.db"
    assert config.ALLOWED_HOSTS == "*"


if __name__ == "__main__":
    # Run basic tests when executed directly
    test_config_imports_successfully()
    test_email_settings_structure()
    test_blob_storage_settings_structure()
    test_application_settings_structure()
    test_application_insights_settings()
    test_logging_settings_structure()
    test_database_connection_string()
    test_diagnostics_and_website_settings()
    test_environment_settings()
    test_all_settings_structure()
    test_hardcoded_values_match_appsettings()
    
    print("✅ All config tests passed!")
    print("🚨 Remember: This config is for DEVELOPMENT/DEBUG only!")