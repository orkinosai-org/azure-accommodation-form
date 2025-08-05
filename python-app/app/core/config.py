"""
Configuration settings for the Azure Accommodation Form application

This module contains all configuration settings that mirror the .NET appsettings.json
structure, providing Python equivalents for logging, email, storage, and other services.
"""

import os
import logging
from enum import Enum
from functools import lru_cache
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


class LogLevel(str, Enum):
    """Log levels that map to both .NET and Python logging"""
    TRACE = "TRACE"  # .NET Trace -> Python DEBUG
    DEBUG = "DEBUG"  # .NET Debug -> Python DEBUG
    INFORMATION = "INFORMATION"  # .NET Information -> Python INFO
    WARNING = "WARNING"  # .NET Warning -> Python WARNING
    ERROR = "ERROR"  # .NET Error -> Python ERROR
    CRITICAL = "CRITICAL"  # .NET Critical -> Python CRITICAL
    
    @property
    def python_level(self) -> int:
        """Convert to Python logging level"""
        mapping = {
            self.TRACE: logging.DEBUG,
            self.DEBUG: logging.DEBUG,
            self.INFORMATION: logging.INFO,
            self.WARNING: logging.WARNING,
            self.ERROR: logging.ERROR,
            self.CRITICAL: logging.CRITICAL
        }
        return mapping.get(self, logging.INFO)


class LoggingSettings(BaseSettings):
    """Logging configuration that mirrors .NET logging structure"""
    
    # Default log levels (mirrors .NET LogLevel section)
    default_level: LogLevel = LogLevel.INFORMATION
    microsoft_level: LogLevel = LogLevel.WARNING
    microsoft_hosting_lifetime_level: LogLevel = LogLevel.INFORMATION
    
    # Console logging settings
    console_include_scopes: bool = False
    console_timestamp_format: str = "HH:mm:ss "
    
    class Config:
        env_prefix = "LOGGING_"


class EmailSettings(BaseSettings):
    """Email/SMTP configuration that mirrors .NET EmailSettings"""
    
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    use_ssl: bool = True  # Maps to UseSsl in .NET
    from_email: str = ""  # Removed noreply@gmail.com fallback
    from_name: str = "Azure Accommodation Form"
    company_email: str = ""  # Maps to CompanyEmail in .NET
    
    class Config:
        env_prefix = "EMAIL_"


class BlobStorageSettings(BaseSettings):
    """Azure Blob Storage configuration that mirrors .NET BlobStorageSettings"""
    
    connection_string: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "form-submissions")
    
    class Config:
        env_prefix = "BLOB_STORAGE_"


class ApplicationSettings(BaseSettings):
    """Application settings that mirror .NET ApplicationSettings"""
    
    application_name: str = os.getenv("APPLICATION_NAME", "Azure Accommodation Form")
    application_url: str = os.getenv("APPLICATION_URL", "http://localhost:8000")
    token_expiration_minutes: int = int(os.getenv("TOKEN_EXPIRATION_MINUTES", "15"))
    token_length: int = int(os.getenv("TOKEN_LENGTH", "6"))
    
    class Config:
        env_prefix = "APPLICATION_"


class ApplicationInsightsSettings(BaseSettings):
    """Application Insights configuration that mirrors .NET ApplicationInsights"""
    
    connection_string: Optional[str] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    agent_extension_version: str = os.getenv("APPLICATIONINSIGHTS_AGENT_VERSION", "~2")
    xdt_mode: str = os.getenv("APPLICATIONINSIGHTS_XDT_MODE", "default")
    
    class Config:
        env_prefix = "APPLICATIONINSIGHTS_"


class DiagnosticsSettings(BaseSettings):
    """Diagnostics configuration that mirrors .NET Diagnostics"""
    
    azure_blob_retention_days: int = int(os.getenv("DIAGNOSTICS_BLOB_RETENTION_DAYS", "2"))
    http_logging_retention_days: int = int(os.getenv("DIAGNOSTICS_HTTP_RETENTION_DAYS", "2"))
    
    class Config:
        env_prefix = "DIAGNOSTICS_"


class Settings(BaseSettings):
    """
    Main application settings class that combines all configuration sections
    This mirrors the structure of appsettings.json from the .NET Blazor application
    """
    
    # Basic application configuration
    app_name: str = "Azure Accommodation Form"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))
    allowed_hosts: list[str] = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    allowed_origins: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # SSL/TLS settings
    ssl_keyfile: Optional[str] = os.getenv("SSL_KEYFILE")
    ssl_certfile: Optional[str] = os.getenv("SSL_CERTFILE")
    
    # Configuration sections that mirror appsettings.json structure
    logging: LoggingSettings = LoggingSettings()
    email_settings: EmailSettings = EmailSettings()
    blob_storage_settings: BlobStorageSettings = BlobStorageSettings()
    application_settings: ApplicationSettings = ApplicationSettings()
    application_insights: ApplicationInsightsSettings = ApplicationInsightsSettings()
    diagnostics: DiagnosticsSettings = DiagnosticsSettings()
    
    # Backward compatibility for existing code
    @property
    def smtp_server(self) -> str:
        return self.email_settings.smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
    
    @property
    def smtp_port(self) -> int:
        return self.email_settings.smtp_port or int(os.getenv("SMTP_PORT", "587"))
    
    @property
    def smtp_username(self) -> str:
        return self.email_settings.smtp_username or os.getenv("SMTP_USERNAME", "")
    
    @property
    def smtp_password(self) -> str:
        return self.email_settings.smtp_password or os.getenv("SMTP_PASSWORD", "")
    
    @property
    def smtp_use_tls(self) -> bool:
        if self.email_settings.use_ssl:
            return self.email_settings.use_ssl
        return os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    @property
    def from_email(self) -> str:
        return self.email_settings.from_email or os.getenv("FROM_EMAIL", "")
    
    @property
    def from_name(self) -> str:
        return self.email_settings.from_name or os.getenv("FROM_NAME", "Azure Accommodation Form")
    
    @property
    def admin_email(self) -> str:
        return self.email_settings.company_email or os.getenv("ADMIN_EMAIL", "admin@yourdomain.com")
    
    @property
    def azure_storage_connection_string(self) -> Optional[str]:
        return self.blob_storage_settings.connection_string
    
    @property
    def azure_storage_container_name(self) -> str:
        return self.blob_storage_settings.container_name
    
    # Legacy settings for backward compatibility
    azure_communication_connection_string: Optional[str] = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    
    # MFA settings (using application_settings for token config)
    @property
    def mfa_token_length(self) -> int:
        return self.application_settings.token_length
    
    @property
    def mfa_token_expiry_minutes(self) -> int:
        return self.application_settings.token_expiration_minutes
    
    # Form settings
    max_address_history_years: int = int(os.getenv("MAX_ADDRESS_HISTORY_YEARS", 3))
    allowed_file_types: list[str] = os.getenv("ALLOWED_FILE_TYPES", "pdf,jpg,jpeg,png").split(",")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get Python logging configuration based on .NET style log levels
        This mimics the behavior of .NET's logging configuration
        """
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': f'{self.logging.console_timestamp_format}%(name)s - %(levelname)s - %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'level': self.logging.default_level.python_level,
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                '': {  # Root logger
                    'handlers': ['console'],
                    'level': self.logging.default_level.python_level,
                    'propagate': False
                },
                'uvicorn': {
                    'handlers': ['console'],
                    'level': self.logging.microsoft_level.python_level,
                    'propagate': False
                },
                'uvicorn.access': {
                    'handlers': ['console'],
                    'level': self.logging.microsoft_hosting_lifetime_level.python_level,
                    'propagate': False
                }
            }
        }
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields for environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()