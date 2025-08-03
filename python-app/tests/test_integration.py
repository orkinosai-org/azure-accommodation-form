"""
Integration tests to verify that all services work with the new configuration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.core.config import get_settings
from app.services.email import EmailService
from app.services.storage import AzureBlobStorageService
from app.services.application_insights import ApplicationInsightsService

def test_email_service_integration():
    """Test that email service properly uses the new configuration structure"""
    settings = get_settings()
    email_service = EmailService()
    
    # Verify service uses the new configuration structure
    assert email_service.smtp_server == settings.email_settings.smtp_server
    assert email_service.smtp_port == settings.email_settings.smtp_port
    assert email_service.use_ssl == settings.email_settings.use_ssl
    assert email_service.from_email == settings.email_settings.from_email
    assert email_service.from_name == settings.email_settings.from_name
    assert email_service.company_email == settings.email_settings.company_email

def test_storage_service_integration():
    """Test that storage service properly uses the new configuration structure"""
    settings = get_settings()
    storage_service = AzureBlobStorageService()
    
    # Verify service uses the new configuration structure
    assert storage_service.connection_string == settings.blob_storage_settings.connection_string
    assert storage_service.container_name == settings.blob_storage_settings.container_name

def test_application_insights_integration():
    """Test that Application Insights service properly uses the new configuration structure"""
    settings = get_settings()
    insights_service = ApplicationInsightsService()
    
    # Verify service uses the new configuration structure
    assert insights_service.connection_string == settings.application_insights.connection_string
    assert insights_service.agent_extension_version == settings.application_insights.agent_extension_version
    assert insights_service.xdt_mode == settings.application_insights.xdt_mode

def test_email_service_with_mock_config():
    """Test email service with mocked configuration"""
    from unittest.mock import Mock
    
    # Create mock settings
    mock_email_settings = Mock()
    mock_email_settings.smtp_server = 'test.smtp.com'
    mock_email_settings.smtp_port = 587
    mock_email_settings.use_ssl = True
    mock_email_settings.from_email = 'test@example.com'
    mock_email_settings.from_name = 'Test Service'
    mock_email_settings.company_email = 'admin@example.com'
    
    # Test that EmailService would use these settings if available
    with patch('app.services.email.get_settings') as mock_get_settings:
        mock_settings = Mock()
        mock_settings.email_settings = mock_email_settings
        mock_get_settings.return_value = mock_settings
        
        email_service = EmailService()
        
        assert email_service.smtp_server == 'test.smtp.com'
        assert email_service.smtp_port == 587
        assert email_service.use_ssl == True
        assert email_service.from_email == 'test@example.com'
        assert email_service.from_name == 'Test Service'
        assert email_service.company_email == 'admin@example.com'

def test_configuration_sections_isolation():
    """Test that configuration sections are properly isolated"""
    settings = get_settings()
    
    # Test that each section is independent
    assert hasattr(settings, 'logging')
    assert hasattr(settings, 'email_settings')
    assert hasattr(settings, 'blob_storage_settings')
    assert hasattr(settings, 'application_settings')
    assert hasattr(settings, 'application_insights')
    assert hasattr(settings, 'diagnostics')
    
    # Test that sections don't interfere with each other
    logging_config = settings.logging
    email_config = settings.email_settings
    
    assert logging_config != email_config
    assert type(logging_config).__name__ == 'LoggingSettings'
    assert type(email_config).__name__ == 'EmailSettings'

def test_dotnet_equivalent_values():
    """Test that default values match .NET appsettings.json"""
    settings = get_settings()
    
    # Application settings should match .NET ApplicationSettings
    assert settings.application_settings.application_name == "Azure Accommodation Form"
    assert settings.application_settings.token_expiration_minutes == 15
    assert settings.application_settings.token_length == 6
    
    # Email settings should match .NET EmailSettings defaults
    assert settings.email_settings.smtp_server == "smtp.gmail.com"
    assert settings.email_settings.smtp_port == 587
    assert settings.email_settings.from_name == "Azure Accommodation Form"
    
    # Diagnostics should match .NET Diagnostics
    assert settings.diagnostics.azure_blob_retention_days == 2
    assert settings.diagnostics.http_logging_retention_days == 2
    
    # Application Insights should match .NET ApplicationInsights defaults
    assert settings.application_insights.agent_extension_version == "~2"
    assert settings.application_insights.xdt_mode == "default"

def test_backward_compatibility_properties():
    """Test that backward compatibility properties work correctly"""
    settings = get_settings()
    
    # Test that old property names still work
    assert settings.smtp_server == settings.email_settings.smtp_server
    assert settings.smtp_port == settings.email_settings.smtp_port
    assert settings.smtp_use_tls == settings.email_settings.use_ssl
    assert settings.from_email == settings.email_settings.from_email
    assert settings.from_name == settings.email_settings.from_name
    
    assert settings.azure_storage_connection_string == settings.blob_storage_settings.connection_string
    assert settings.azure_storage_container_name == settings.blob_storage_settings.container_name
    
    assert settings.mfa_token_length == settings.application_settings.token_length
    assert settings.mfa_token_expiry_minutes == settings.application_settings.token_expiration_minutes

if __name__ == "__main__":
    pytest.main([__file__])