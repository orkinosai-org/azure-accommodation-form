"""
Tests for configuration settings that mirror .NET appsettings.json
"""

import pytest
import os
from app.core.config import get_settings, LogLevel

def test_config_loading():
    """Test that configuration loads properly"""
    settings = get_settings()
    assert settings.app_name == "Azure Accommodation Form"
    assert isinstance(settings.port, int)

def test_logging_config_structure():
    """Test that logging configuration mirrors .NET structure"""
    settings = get_settings()
    
    # Test logging settings
    assert hasattr(settings.logging, 'default_level')
    assert hasattr(settings.logging, 'microsoft_level')
    assert hasattr(settings.logging, 'console_timestamp_format')
    
    # Test log level mapping
    assert LogLevel.INFORMATION.python_level == 20  # INFO level
    assert LogLevel.WARNING.python_level == 30     # WARNING level
    assert LogLevel.ERROR.python_level == 40       # ERROR level

def test_email_settings_structure():
    """Test that email settings mirror .NET EmailSettings"""
    settings = get_settings()
    
    # Test email settings structure
    assert hasattr(settings.email_settings, 'smtp_server')
    assert hasattr(settings.email_settings, 'smtp_port')
    assert hasattr(settings.email_settings, 'use_ssl')  # Maps to .NET UseSsl
    assert hasattr(settings.email_settings, 'from_email')
    assert hasattr(settings.email_settings, 'from_name')
    assert hasattr(settings.email_settings, 'company_email')  # Maps to .NET CompanyEmail

def test_blob_storage_settings_structure():
    """Test that blob storage settings mirror .NET BlobStorageSettings"""
    settings = get_settings()
    
    # Test blob storage settings structure
    assert hasattr(settings.blob_storage_settings, 'connection_string')
    assert hasattr(settings.blob_storage_settings, 'container_name')
    
    # Test default values
    assert settings.blob_storage_settings.container_name == "form-submissions"

def test_application_settings_structure():
    """Test that application settings mirror .NET ApplicationSettings"""
    settings = get_settings()
    
    # Test application settings structure
    assert hasattr(settings.application_settings, 'application_name')
    assert hasattr(settings.application_settings, 'application_url')
    assert hasattr(settings.application_settings, 'token_expiration_minutes')
    assert hasattr(settings.application_settings, 'token_length')
    
    # Test default values
    assert settings.application_settings.application_name == "Azure Accommodation Form"
    assert settings.application_settings.token_length == 6
    assert settings.application_settings.token_expiration_minutes == 15

def test_application_insights_structure():
    """Test that Application Insights settings mirror .NET ApplicationInsights"""
    settings = get_settings()
    
    # Test Application Insights settings structure
    assert hasattr(settings.application_insights, 'connection_string')
    assert hasattr(settings.application_insights, 'agent_extension_version')
    assert hasattr(settings.application_insights, 'xdt_mode')
    
    # Test default values
    assert settings.application_insights.agent_extension_version == "~2"
    assert settings.application_insights.xdt_mode == "default"

def test_diagnostics_settings_structure():
    """Test that diagnostics settings mirror .NET Diagnostics"""
    settings = get_settings()
    
    # Test diagnostics settings structure
    assert hasattr(settings.diagnostics, 'azure_blob_retention_days')
    assert hasattr(settings.diagnostics, 'http_logging_retention_days')
    
    # Test default values
    assert settings.diagnostics.azure_blob_retention_days == 2
    assert settings.diagnostics.http_logging_retention_days == 2

def test_backward_compatibility():
    """Test that backward compatibility properties work"""
    settings = get_settings()
    
    # Test that old property names still work
    assert settings.smtp_server == settings.email_settings.smtp_server
    assert settings.smtp_port == settings.email_settings.smtp_port
    assert settings.smtp_use_tls == settings.email_settings.use_ssl
    assert settings.azure_storage_connection_string == settings.blob_storage_settings.connection_string
    assert settings.mfa_token_length == settings.application_settings.token_length

def test_logging_config_generation():
    """Test that Python logging configuration is properly generated"""
    settings = get_settings()
    
    logging_config = settings.get_logging_config()
    
    # Test structure
    assert 'version' in logging_config
    assert 'formatters' in logging_config
    assert 'handlers' in logging_config
    assert 'loggers' in logging_config
    
    # Test console formatter includes timestamp format
    console_formatter = logging_config['formatters']['standard']['format']
    assert settings.logging.console_timestamp_format in console_formatter

def test_environment_variables():
    """Test that environment variables are properly loaded"""
    # Test that we can load environment variables
    environment = os.getenv("ENVIRONMENT", "development")
    assert environment in ["development", "production", "testing"]

if __name__ == "__main__":
    pytest.main([__file__])