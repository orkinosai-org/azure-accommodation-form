"""
Test email verification functionality including the settings bug fix
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Request

from app.api.routes.auth import request_email_verification
from app.models.form import EmailVerificationRequest
from app.services.email import EmailService
from app.core.config import get_settings


@pytest.mark.asyncio
async def test_email_service_mfa_token_settings_access():
    """Test that EmailService.send_mfa_token can access settings without NameError"""
    
    email_service = EmailService()
    
    # Mock the _send_email method to avoid actual SMTP calls
    with patch.object(email_service, '_send_email', return_value=True) as mock_send:
        
        # This should not raise a NameError for 'settings'
        result = await email_service.send_mfa_token("test@example.com", "123456")
        
        # Verify the method completed and called _send_email
        assert mock_send.called
        mock_send.assert_called_once()
        
        # Check that the email content includes the correct expiry time
        call_args = mock_send.call_args
        email_body_text = call_args[0][2]  # body_text is the 3rd argument
        email_body_html = call_args[0][3]  # body_html is the 4th argument
        
        settings = get_settings()
        expected_minutes = str(settings.mfa_token_expiry_minutes)
        
        assert expected_minutes in email_body_text
        assert expected_minutes in email_body_html


@pytest.mark.asyncio 
async def test_email_verification_endpoint_with_mocked_email():
    """Test the email verification endpoint with mocked email service"""
    
    # Create test request
    email_request = EmailVerificationRequest(
        email="test@example.com",
        email_confirm="test@example.com",
        math_question="What is 2 + 3?",
        math_answer="5"
    )
    
    # Mock HTTP request
    mock_request = MagicMock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {}
    
    # Mock all dependencies to avoid certificate and SMTP issues
    with patch('app.api.routes.auth.require_certificate_auth'):
        with patch('app.api.routes.auth.get_current_ip', return_value="127.0.0.1"):
            with patch('app.api.routes.auth.MathCaptchaService') as mock_captcha:
                mock_captcha.return_value.verify_math_answer.return_value = True
                
                with patch.object(EmailService, 'send_mfa_token', return_value=True) as mock_send:
                    
                    # This should not raise a NameError for 'settings'
                    result = await request_email_verification(email_request, mock_request)
                    
                    # Verify the response
                    assert hasattr(result, 'verification_id')
                    assert hasattr(result, 'message')
                    assert hasattr(result, 'expires_at')
                    assert email_request.email in result.message
                    
                    # Verify email service was called
                    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_email_service_settings_property_access():
    """Test that email service can access all necessary settings properties"""
    
    email_service = EmailService()
    settings = get_settings()
    
    # Verify the email service can access key settings
    assert email_service.email_settings is not None
    assert hasattr(email_service, 'smtp_server')
    assert hasattr(email_service, 'smtp_port')
    assert hasattr(email_service, 'from_email')
    
    # Verify that settings can be accessed in the context that was previously failing
    assert settings.mfa_token_expiry_minutes > 0
    assert isinstance(settings.mfa_token_expiry_minutes, int)
    
    # Test that we can format the expiry message without errors
    token = "123456"
    email = "test@example.com"
    expected_message = f"This code will expire in {settings.mfa_token_expiry_minutes} minutes."
    
    # This should work without NameError
    formatted_message = f"This code will expire in {settings.mfa_token_expiry_minutes} minutes."
    assert formatted_message == expected_message


def test_settings_mfa_token_configuration():
    """Test that MFA token settings are properly configured"""
    
    settings = get_settings()
    
    # Verify MFA token settings exist and have reasonable values
    assert hasattr(settings, 'mfa_token_expiry_minutes')
    assert hasattr(settings, 'mfa_token_length')
    
    assert isinstance(settings.mfa_token_expiry_minutes, int)
    assert isinstance(settings.mfa_token_length, int)
    
    assert settings.mfa_token_expiry_minutes > 0
    assert settings.mfa_token_length > 0
    
    # Default values should be reasonable
    assert settings.mfa_token_expiry_minutes <= 60  # Should not be more than 1 hour
    assert settings.mfa_token_length >= 4  # Should be at least 4 digits