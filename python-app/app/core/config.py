"""
Configuration settings for the Azure Accommodation Form application
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
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
    
    # Email settings
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    from_email: str = os.getenv("FROM_EMAIL", "noreply@yourdomain.com")
    from_name: str = os.getenv("FROM_NAME", "Azure Accommodation Form")
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@yourdomain.com")
    
    # Azure Communication Services (alternative to SMTP)
    azure_communication_connection_string: Optional[str] = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    
    # Azure Blob Storage settings
    azure_storage_connection_string: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    azure_storage_container_name: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "form-submissions")
    
    # CAPTCHA settings
    captcha_site_key: str = os.getenv("CAPTCHA_SITE_KEY", "")
    captcha_secret_key: str = os.getenv("CAPTCHA_SECRET_KEY", "")
    captcha_provider: str = os.getenv("CAPTCHA_PROVIDER", "recaptcha")  # recaptcha or hcaptcha
    
    # MFA settings
    mfa_token_length: int = int(os.getenv("MFA_TOKEN_LENGTH", 6))
    mfa_token_expiry_minutes: int = int(os.getenv("MFA_TOKEN_EXPIRY_MINUTES", 10))
    
    # Form settings
    max_address_history_years: int = int(os.getenv("MAX_ADDRESS_HISTORY_YEARS", 3))
    allowed_file_types: list[str] = os.getenv("ALLOWED_FILE_TYPES", "pdf,jpg,jpeg,png").split(",")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()