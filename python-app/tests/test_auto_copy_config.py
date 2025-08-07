"""
Tests for automatic copying of appsettings.example.json to appsettings.json when missing
"""

import os
import json
import pytest
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.core.config import load_config_from_file, get_settings


def test_auto_copy_when_appsettings_missing_but_example_exists():
    """Test that appsettings.example.json is automatically copied when appsettings.json is missing"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "appsettings.json"
        example_file = temp_path / "appsettings.example.json"
        
        # Create a valid example config
        example_config = {
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
        
        # Write the example file
        with open(example_file, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        # Ensure appsettings.json doesn't exist
        assert not config_file.exists()
        assert example_file.exists()
        
        # Mock logger to capture warning messages
        with patch('app.core.config.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Load config from the directory
            config_data = load_config_from_file(str(config_file))
            
            # Verify the file was copied
            assert config_file.exists()
            
            # Verify the warning was logged
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "was missing" in warning_call
            assert "Automatically copied" in warning_call
            assert "appsettings.example.json" in warning_call
            
            # Verify the config data is correct
            assert config_data == example_config


def test_no_auto_copy_when_appsettings_exists():
    """Test that no auto-copy occurs when appsettings.json already exists"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "appsettings.json"
        example_file = temp_path / "appsettings.example.json"
        
        # Create both files with different content
        main_config = {
            "EmailSettings": {
                "SmtpServer": "main.smtp.com",
                "SmtpPort": 25,
                "SmtpUsername": "main@example.com",
                "SmtpPassword": "main-password",
                "UseSsl": False,
                "FromEmail": "main-from@example.com",
                "FromName": "Main App",
                "CompanyEmail": "main-company@example.com"
            }
        }
        
        example_config = {
            "EmailSettings": {
                "SmtpServer": "example.smtp.com",
                "SmtpPort": 587,
                "SmtpUsername": "example@example.com",
                "SmtpPassword": "example-password",
                "UseSsl": True,
                "FromEmail": "example-from@example.com",
                "FromName": "Example App",
                "CompanyEmail": "example-company@example.com"
            }
        }
        
        # Write both files
        with open(config_file, 'w') as f:
            json.dump(main_config, f, indent=2)
        with open(example_file, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        # Mock logger to ensure no warning is logged
        with patch('app.core.config.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Load config
            config_data = load_config_from_file(str(config_file))
            
            # Verify no warning was logged
            mock_logger.warning.assert_not_called()
            
            # Verify the main config is loaded, not the example
            assert config_data == main_config
            assert config_data != example_config


def test_error_when_neither_file_exists():
    """Test that appropriate error is raised when neither file exists"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "appsettings.json"
        example_file = temp_path / "appsettings.example.json"
        
        # Ensure neither file exists
        assert not config_file.exists()
        assert not example_file.exists()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            load_config_from_file(str(config_file))
        
        error_message = str(exc_info.value)
        assert "not found" in error_message
        assert "appsettings.example.json" in error_message
        assert "Unable to find Blazor app configuration" in error_message


def test_error_when_copy_fails():
    """Test that appropriate error is raised when copy operation fails"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "appsettings.json"
        example_file = temp_path / "appsettings.example.json"
        
        # Create example file
        example_config = {"test": "data"}
        with open(example_file, 'w') as f:
            json.dump(example_config, f)
        
        # Mock shutil.copy2 to raise an exception
        with patch('shutil.copy2') as mock_copy:
            mock_copy.side_effect = PermissionError("Permission denied")
            
            with pytest.raises(RuntimeError) as exc_info:
                load_config_from_file(str(config_file))
            
            error_message = str(exc_info.value)
            assert "Failed to auto-copy" in error_message
            assert "Permission denied" in error_message
            assert "manually copy" in error_message


def test_integration_with_get_settings():
    """Test that the auto-copy feature works with get_settings function"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a complete valid example config
        example_config = {
            "Logging": {
                "LogLevel": {
                    "Default": "Information",
                    "Microsoft": "Warning",
                    "Microsoft.Hosting.Lifetime": "Information"
                },
                "Console": {
                    "IncludeScopes": False,
                    "TimestampFormat": "HH:mm:ss "
                }
            },
            "EmailSettings": {
                "SmtpServer": "smtp.gmail.com",
                "SmtpPort": 587,
                "SmtpUsername": "test@example.com",
                "SmtpPassword": "test-password",
                "UseSsl": True,
                "FromEmail": "from@example.com",
                "FromName": "Test App",
                "CompanyEmail": "company@example.com"
            },
            "BlobStorageSettings": {
                "ConnectionString": "test-connection-string",
                "ContainerName": "test-container"
            },
            "ApplicationSettings": {
                "ApplicationName": "Test Application",
                "ApplicationUrl": "http://localhost:8000",
                "TokenExpirationMinutes": 15,
                "TokenLength": 6
            },
            "ApplicationInsights": {
                "ConnectionString": "test-insights-connection",
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
                "SecretKey": "test-secret-key",
                "Host": "0.0.0.0",
                "Port": 8000,
                "AllowedHosts": ["localhost", "127.0.0.1"],
                "AllowedOrigins": ["http://localhost:8000"],
                "SslKeyfile": None,
                "SslCertfile": None
            }
        }
        
        # Save original working directory and change to temp directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create example file
            with open("appsettings.example.json", 'w') as f:
                json.dump(example_config, f, indent=2)
            
            # Ensure appsettings.json doesn't exist
            assert not Path("appsettings.json").exists()
            
            # Clear the cache to force reload
            get_settings.cache_clear()
            
            # Mock logger to capture warning
            with patch('app.core.config.logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                # Get settings should trigger auto-copy
                settings = get_settings()
                
                # Verify the file was created
                assert Path("appsettings.json").exists()
                
                # Verify warning was logged
                mock_logger.warning.assert_called()
                
                # Verify settings are loaded correctly
                assert settings.application_settings.application_name == "Test Application"
                assert settings.email_settings.smtp_server == "smtp.gmail.com"
                assert settings.server_settings.environment == "development"
        
        finally:
            # Restore working directory and clear cache
            os.chdir(old_cwd)
            get_settings.cache_clear()


def test_auto_copy_preserves_file_permissions():
    """Test that auto-copy preserves file permissions using shutil.copy2"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "appsettings.json"
        example_file = temp_path / "appsettings.example.json"
        
        # Create example file
        example_config = {"test": "data"}
        with open(example_file, 'w') as f:
            json.dump(example_config, f)
        
        # Track if copy2 was called
        import shutil
        original_copy2 = shutil.copy2
        copy2_called = []
        
        def mock_copy2(src, dst):
            copy2_called.append((src, dst))
            return original_copy2(src, dst)
        
        # Mock shutil.copy2 to verify it's called
        with patch('shutil.copy2', side_effect=mock_copy2):
            load_config_from_file(str(config_file))
            
            # Verify copy2 was called (preserves metadata)
            assert len(copy2_called) == 1
            assert str(copy2_called[0][0]) == str(example_file)
            assert str(copy2_called[0][1]) == str(config_file)


def test_auto_copy_from_blazor_config_when_appsettings_missing():
    """Test that Blazor app's appsettings.json is automatically copied when Python app's appsettings.json is missing"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        python_app_dir = temp_path / "python-app"
        blazor_app_dir = temp_path / "BlazorApp"
        
        # Create directory structure
        python_app_dir.mkdir()
        blazor_app_dir.mkdir()
        
        config_file = python_app_dir / "appsettings.json"
        blazor_config_file = blazor_app_dir / "appsettings.json"
        
        # Create a valid Blazor config with production-ready settings
        blazor_config = {
            "Logging": {
                "LogLevel": {
                    "Default": "Information",
                    "Microsoft": "Warning",
                    "Microsoft.Hosting.Lifetime": "Information"
                },
                "Console": {
                    "IncludeScopes": False,
                    "TimestampFormat": "HH:mm:ss "
                }
            },
            "AllowedHosts": "*",
            "ConnectionStrings": {
                "DefaultConnection": "Data Source=FormSubmissions.db"
            },
            "EmailSettings": {
                "SmtpServer": "smtp.gmail.com",
                "SmtpPort": 587,
                "SmtpUsername": "production@example.com",
                "SmtpPassword": "production-password",
                "UseSsl": True,
                "FromEmail": "noreply@production.com",
                "FromName": "Azure Accommodation Form",
                "CompanyEmail": "admin@production.com"
            },
            "BlobStorageSettings": {
                "ConnectionString": "production-storage-connection-string",
                "ContainerName": "form-submissions"
            },
            "ApplicationSettings": {
                "ApplicationName": "Azure Accommodation Form",
                "ApplicationUrl": "https://production.azurewebsites.net/",
                "TokenExpirationMinutes": 15,
                "TokenLength": 6
            },
            "ApplicationInsights": {
                "ConnectionString": "production-insights-connection",
                "AgentExtensionVersion": "~2",
                "XDT_Mode": "default"
            },
            "Diagnostics": {
                "AzureBlobRetentionInDays": 2
            },
            "Website": {
                "HttpLoggingRetentionDays": 2
            }
        }
        
        # Write the Blazor config file
        with open(blazor_config_file, 'w') as f:
            json.dump(blazor_config, f, indent=2)
        
        # Ensure Python app's appsettings.json doesn't exist
        assert not config_file.exists()
        assert blazor_config_file.exists()
        
        # Change to python-app directory for relative path resolution
        old_cwd = os.getcwd()
        os.chdir(python_app_dir)
        
        try:
            # Mock logger to capture info messages
            with patch('app.core.config.logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                # Load config from the python-app directory
                config_data = load_config_from_file("appsettings.json")
                
                # Verify the file was copied
                assert config_file.exists()
                
                # Verify the info message was logged (not warning since this is preferred behavior)
                mock_logger.info.assert_called_once()
                info_call = mock_logger.info.call_args[0][0]
                assert "was missing" in info_call
                assert "Automatically copied production-ready configuration from Blazor app" in info_call
                assert "adapted it for Python app requirements" in info_call
                assert "Added ServerSettings section" in info_call
                
                # Verify the config data includes both Blazor settings and added ServerSettings
                assert "EmailSettings" in config_data
                assert "ServerSettings" in config_data
                assert config_data["EmailSettings"]["SmtpUsername"] == "production@example.com"
                assert config_data["ApplicationSettings"]["ApplicationUrl"] == "https://production.azurewebsites.net/"
                assert config_data["ServerSettings"]["Environment"] == "production"
                assert config_data["ServerSettings"]["Host"] == "0.0.0.0"
        
        finally:
            os.chdir(old_cwd)


def test_blazor_config_takes_priority_over_example():
    """Test that Blazor config is preferred over example config when both exist and appsettings.json is missing"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        python_app_dir = temp_path / "python-app" 
        blazor_app_dir = temp_path / "BlazorApp"
        
        # Create directory structure
        python_app_dir.mkdir()
        blazor_app_dir.mkdir()
        
        config_file = python_app_dir / "appsettings.json"
        example_file = python_app_dir / "appsettings.example.json"
        blazor_config_file = blazor_app_dir / "appsettings.json"
        
        # Create different configs
        blazor_config = {
            "EmailSettings": {
                "SmtpServer": "blazor.smtp.com",
                "SmtpUsername": "blazor@example.com",
                "SmtpPassword": "blazor-password"
            },
            "ApplicationSettings": {
                "ApplicationUrl": "https://blazor-production.com"
            }
        }
        
        example_config = {
            "EmailSettings": {
                "SmtpServer": "example.smtp.com", 
                "SmtpUsername": "example@example.com",
                "SmtpPassword": "example-password"
            },
            "ApplicationSettings": {
                "ApplicationUrl": "http://localhost:8000"
            }
        }
        
        # Write both files
        with open(blazor_config_file, 'w') as f:
            json.dump(blazor_config, f, indent=2)
        with open(example_file, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        # Ensure Python app's appsettings.json doesn't exist
        assert not config_file.exists()
        assert blazor_config_file.exists()
        assert example_file.exists()
        
        # Change to python-app directory for relative path resolution
        old_cwd = os.getcwd()
        os.chdir(python_app_dir)
        
        try:
            # Mock logger to capture messages
            with patch('app.core.config.logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                # Load config
                config_data = load_config_from_file("appsettings.json")
                
                # Verify Blazor config was used as base, with ServerSettings added
                assert config_data != example_config
                assert config_data["EmailSettings"]["SmtpUsername"] == "blazor@example.com"
                assert config_data["ApplicationSettings"]["ApplicationUrl"] == "https://blazor-production.com"
                assert "ServerSettings" in config_data
                assert config_data["ServerSettings"]["Environment"] == "production"
                
                # Verify info message was logged about Blazor config
                mock_logger.info.assert_called_once()
                info_call = mock_logger.info.call_args[0][0]
                assert "Blazor app" in info_call
                
        finally:
            os.chdir(old_cwd)


def test_fallback_to_example_when_blazor_config_missing():
    """Test that it falls back to example config when Blazor config is not available"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        python_app_dir = temp_path / "python-app"
        
        # Create only python-app directory (no BlazorApp)
        python_app_dir.mkdir()
        
        config_file = python_app_dir / "appsettings.json"
        example_file = python_app_dir / "appsettings.example.json"
        
        # Create only example config
        example_config = {
            "EmailSettings": {
                "SmtpServer": "example.smtp.com",
                "SmtpUsername": "example@example.com",
                "SmtpPassword": "example-password"
            }
        }
        
        with open(example_file, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        # Ensure Python app's appsettings.json doesn't exist
        assert not config_file.exists()
        assert example_file.exists()
        
        # Change to python-app directory for relative path resolution
        old_cwd = os.getcwd()
        os.chdir(python_app_dir)
        
        try:
            # Mock logger to capture warning messages
            with patch('app.core.config.logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                # Load config
                config_data = load_config_from_file("appsettings.json")
                
                # Verify example config was used
                assert config_data == example_config
                
                # Verify warning message was logged about using example as fallback
                mock_logger.warning.assert_called_once()
                warning_call = mock_logger.warning.call_args[0][0]
                assert "Blazor app config not found" in warning_call
                assert "appsettings.example.json" in warning_call
                
        finally:
            os.chdir(old_cwd)