"""
Tests to verify that the configuration system ONLY uses appsettings.json 
and completely ignores environment variables and .env files.
"""

import os
import pytest
import tempfile
import json
from unittest.mock import patch
from pathlib import Path

from app.core.config import get_settings, load_config_from_file, create_settings_from_config


def test_appsettings_json_file_required():
    """Test that appsettings.json file is required and FileNotFoundError is raised if missing"""
    
    # Test with non-existent config file
    with pytest.raises(FileNotFoundError) as exc_info:
        load_config_from_file("nonexistent.json")
    
    assert "Configuration file 'nonexistent.json' not found" in str(exc_info.value)
    assert "appsettings.example.json" in str(exc_info.value)


def test_appsettings_json_invalid_json():
    """Test that invalid JSON in appsettings file raises ValueError"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{ invalid json content }')
        temp_config_path = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            load_config_from_file(temp_config_path)
        
        assert "Invalid JSON in configuration file" in str(exc_info.value)
    finally:
        os.unlink(temp_config_path)


def test_email_config_required_fields_validation():
    """Test that missing required email fields cause ValueError"""
    
    # Create minimal config with missing email fields
    config_data = {
        "EmailSettings": {
            "SmtpServer": "smtp.gmail.com",
            "SmtpPort": 587,
            # Missing required fields: SmtpUsername, SmtpPassword, FromEmail, CompanyEmail
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_config_path = f.name
    
    try:
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        with patch('app.core.config.load_config_from_file') as mock_load:
            mock_load.return_value = config_data
            
            with pytest.raises(ValueError) as exc_info:
                get_settings()
            
            assert "Missing required email configuration fields" in str(exc_info.value)
            assert "SmtpUsername" in str(exc_info.value)
            assert "SmtpPassword" in str(exc_info.value)
            assert "FromEmail" in str(exc_info.value)
            assert "CompanyEmail" in str(exc_info.value)
    finally:
        os.unlink(temp_config_path)
        get_settings.cache_clear()


def test_environment_variables_completely_ignored():
    """Test that environment variables are completely ignored, even if set"""
    
    # Set environment variables that would have been used in the old system
    env_vars = {
        'EMAIL_SMTP_SERVER': 'env-smtp.example.com',
        'EMAIL_SMTP_PORT': '999',
        'EMAIL_SMTP_USERNAME': 'env-user@example.com',
        'EMAIL_SMTP_PASSWORD': 'env-password',
        'EMAIL_FROM_EMAIL': 'env-from@example.com',
        'EMAIL_COMPANY_EMAIL': 'env-company@example.com',
        'SMTP_SERVER': 'legacy-smtp.example.com',
        'SMTP_USERNAME': 'legacy-user@example.com',
        'SMTP_PASSWORD': 'legacy-password',
        'FROM_EMAIL': 'legacy-from@example.com',
        'ADMIN_EMAIL': 'legacy-admin@example.com',
        'APPLICATION_NAME': 'ENV Application Name',
        'APPLICATION_URL': 'http://env.example.com',
        'ENVIRONMENT': 'production',
        'PORT': '9999',
    }
    
    # Create valid appsettings.json data 
    config_data = {
        "EmailSettings": {
            "SmtpServer": "config-smtp.example.com",
            "SmtpPort": 587,
            "SmtpUsername": "config-user@example.com",
            "SmtpPassword": "config-password",
            "UseSsl": True,
            "FromEmail": "config-from@example.com",
            "FromName": "Config Application",
            "CompanyEmail": "config-company@example.com"
        },
        "ApplicationSettings": {
            "ApplicationName": "Config Application Name",
            "ApplicationUrl": "http://config.example.com"
        },
        "ServerSettings": {
            "Environment": "development",
            "Port": 8000
        }
    }
    
    with patch.dict(os.environ, env_vars):
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        with patch('app.core.config.load_config_from_file') as mock_load:
            mock_load.return_value = config_data
            
            settings = get_settings()
            
            # Verify that ONLY appsettings.json values are used, not environment variables
            assert settings.email_settings.smtp_server == "config-smtp.example.com"
            assert settings.email_settings.smtp_port == 587
            assert settings.email_settings.smtp_username == "config-user@example.com"
            assert settings.email_settings.smtp_password == "config-password"
            assert settings.email_settings.from_email == "config-from@example.com"
            assert settings.email_settings.company_email == "config-company@example.com"
            
            # Test backward compatibility properties also use config values
            assert settings.smtp_server == "config-smtp.example.com"
            assert settings.smtp_username == "config-user@example.com"
            assert settings.from_email == "config-from@example.com"
            assert settings.admin_email == "config-company@example.com"
            
            # Verify environment variables are NOT used
            assert settings.email_settings.smtp_server != "env-smtp.example.com"
            assert settings.email_settings.smtp_server != "legacy-smtp.example.com"
            assert settings.email_settings.smtp_username != "env-user@example.com"
            assert settings.email_settings.smtp_username != "legacy-user@example.com"
    
    get_settings.cache_clear()


def test_dotenv_files_ignored():
    """Test that .env files are completely ignored"""
    
    # Create a .env file with email configuration
    env_content = """
EMAIL_SMTP_SERVER=dotenv-smtp.example.com
EMAIL_SMTP_USERNAME=dotenv-user@example.com
EMAIL_SMTP_PASSWORD=dotenv-password
EMAIL_FROM_EMAIL=dotenv-from@example.com
EMAIL_COMPANY_EMAIL=dotenv-company@example.com
SMTP_SERVER=dotenv-legacy-smtp.example.com
APPLICATION_NAME=Dotenv Application
"""
    
    # Create valid appsettings.json data
    config_data = {
        "EmailSettings": {
            "SmtpServer": "config-smtp.example.com",
            "SmtpPort": 587,
            "SmtpUsername": "config-user@example.com",
            "SmtpPassword": "config-password",
            "UseSsl": True,
            "FromEmail": "config-from@example.com",
            "FromName": "Config Application",
            "CompanyEmail": "config-company@example.com"
        }
    }
    
    # Create temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(env_content)
        env_file_path = f.name
    
    try:
        # Change to the directory containing the .env file
        old_cwd = os.getcwd()
        env_dir = os.path.dirname(env_file_path)
        env_file_name = os.path.basename(env_file_path)
        
        os.chdir(env_dir)
        
        # Rename to .env in current directory
        os.rename(env_file_name, '.env')
        
        # Clear the cache and test
        get_settings.cache_clear()
        
        with patch('app.core.config.load_config_from_file') as mock_load:
            mock_load.return_value = config_data
            
            settings = get_settings()
            
            # Verify that ONLY appsettings.json values are used, not .env file values
            assert settings.email_settings.smtp_server == "config-smtp.example.com"
            assert settings.email_settings.smtp_username == "config-user@example.com"
            
            # Verify .env values are NOT used
            assert settings.email_settings.smtp_server != "dotenv-smtp.example.com"
            assert settings.email_settings.smtp_username != "dotenv-user@example.com"
    
    finally:
        # Cleanup
        os.chdir(old_cwd)
        try:
            os.unlink(os.path.join(env_dir, '.env'))
        except FileNotFoundError:
            pass
        get_settings.cache_clear()


def test_config_audit_shows_json_source():
    """Test that configuration audit shows appsettings.json as the source"""
    
    config_data = {
        "EmailSettings": {
            "SmtpServer": "smtp.gmail.com",
            "SmtpPort": 587,
            "SmtpUsername": "test@example.com",
            "SmtpPassword": "test-password",
            "UseSsl": True,
            "FromEmail": "from@example.com",
            "FromName": "Test App",
            "CompanyEmail": "company@example.com"
        }
    }
    
    get_settings.cache_clear()
    
    with patch('app.core.config.load_config_from_file') as mock_load:
        mock_load.return_value = config_data
        
        settings = get_settings()
        audit_info = settings.audit_configuration()
        
        # Verify audit info shows appsettings.json as source
        assert audit_info["config_source"] == "appsettings.json"
        assert len(audit_info["missing_fields"]) == 0
        assert len(audit_info["warnings"]) == 0
    
    get_settings.cache_clear()


def test_missing_config_fields_clear_error_messages():
    """Test that missing config fields provide clear guidance"""
    
    config_data = {
        "EmailSettings": {
            "SmtpServer": "smtp.gmail.com",
            "SmtpPort": 587,
            # Missing required fields
        }
    }
    
    get_settings.cache_clear()
    
    with patch('app.core.config.load_config_from_file') as mock_load:
        mock_load.return_value = config_data
        
        settings = create_settings_from_config(config_data)
        audit_info = settings.audit_configuration()
        
        # Verify clear guidance is provided for missing fields
        assert len(audit_info["missing_fields"]) == 4
        
        missing_field_names = [field["field"] for field in audit_info["missing_fields"]]
        assert "smtp_username" in missing_field_names
        assert "smtp_password" in missing_field_names
        assert "from_email" in missing_field_names
        assert "company_email" in missing_field_names
        
        # Verify config keys are provided
        for field in audit_info["missing_fields"]:
            assert "config_key" in field
            assert field["config_key"].startswith("Smtp") or field["config_key"].startswith("From") or field["config_key"].startswith("Company")
    
    get_settings.cache_clear()