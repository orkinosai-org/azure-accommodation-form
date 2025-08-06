"""
Configuration settings for the Azure Accommodation Form application

This module loads all configuration from config.json file only, matching the .NET 
appsettings.json structure. No environment variables or .env files are used.
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Optional, Dict, Any, List
from pathlib import Path


class LogLevel(str, Enum):
    """Log levels that map to both .NET and Python logging"""
    TRACE = "Trace"  # .NET Trace -> Python DEBUG
    DEBUG = "Debug"  # .NET Debug -> Python DEBUG  
    INFORMATION = "Information"  # .NET Information -> Python INFO
    WARNING = "Warning"  # .NET Warning -> Python WARNING
    ERROR = "Error"  # .NET Error -> Python ERROR
    CRITICAL = "Critical"  # .NET Critical -> Python CRITICAL
    
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


@dataclass
class LoggingSettings:
    """Logging configuration that mirrors .NET logging structure"""
    default_level: LogLevel = LogLevel.INFORMATION
    microsoft_level: LogLevel = LogLevel.WARNING
    microsoft_hosting_lifetime_level: LogLevel = LogLevel.INFORMATION
    console_include_scopes: bool = False
    console_timestamp_format: str = "HH:mm:ss "


@dataclass
class EmailSettings:
    """Email/SMTP configuration that mirrors .NET EmailSettings exactly"""
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    use_ssl: bool = True  # Maps to UseSsl in .NET
    from_email: str = ""  # Maps to FromEmail in .NET
    from_name: str = "Azure Accommodation Form"  # Maps to FromName in .NET
    company_email: str = ""  # Maps to CompanyEmail in .NET


@dataclass
class BlobStorageSettings:
    """Azure Blob Storage configuration that mirrors .NET BlobStorageSettings"""
    connection_string: Optional[str] = None
    container_name: str = "form-submissions"


@dataclass
class ApplicationSettings:
    """Application settings that mirror .NET ApplicationSettings"""
    application_name: str = "Azure Accommodation Form"
    application_url: str = "http://localhost:8000"
    token_expiration_minutes: int = 15
    token_length: int = 6


@dataclass
class ApplicationInsightsSettings:
    """Application Insights configuration that mirrors .NET ApplicationInsights"""
    connection_string: Optional[str] = None
    agent_extension_version: str = "~2"
    xdt_mode: str = "default"


@dataclass
class DiagnosticsSettings:
    """Diagnostics configuration that mirrors .NET Diagnostics"""
    azure_blob_retention_days: int = 2
    http_logging_retention_days: int = 2


@dataclass
class WebsiteSettings:
    """Website configuration that mirrors .NET Website"""
    http_logging_retention_days: int = 2


@dataclass
class ServerSettings:
    """Server-specific settings for the Python app"""
    environment: str = "development"
    secret_key: str = "your-secret-key-change-in-production"
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_hosts: List[str] = None
    allowed_origins: List[str] = None
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    
    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = ["localhost", "127.0.0.1"]
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:8000", "http://127.0.0.1:8000"]


@dataclass
class Settings:
    """
    Main application settings class that loads configuration from config.json only.
    This mirrors the structure of appsettings.json from the .NET Blazor application.
    """
    
    # Configuration sections that mirror appsettings.json structure
    logging: LoggingSettings
    email_settings: EmailSettings
    blob_storage_settings: BlobStorageSettings
    application_settings: ApplicationSettings
    application_insights: ApplicationInsightsSettings
    diagnostics: DiagnosticsSettings
    website: WebsiteSettings
    server_settings: ServerSettings
    
    # Properties for backward compatibility
    @property
    def app_name(self) -> str:
        return self.application_settings.application_name
    
    @property
    def environment(self) -> str:
        return self.server_settings.environment
    
    @property
    def debug(self) -> bool:
        return self.server_settings.environment == "development"
    
    @property
    def secret_key(self) -> str:
        return self.server_settings.secret_key
    
    @property
    def host(self) -> str:
        return self.server_settings.host
    
    @property
    def port(self) -> int:
        return self.server_settings.port
    
    @property
    def allowed_hosts(self) -> List[str]:
        return self.server_settings.allowed_hosts
    
    @property
    def allowed_origins(self) -> List[str]:
        return self.server_settings.allowed_origins
    
    @property
    def ssl_keyfile(self) -> Optional[str]:
        return self.server_settings.ssl_keyfile
    
    @property
    def ssl_certfile(self) -> Optional[str]:
        return self.server_settings.ssl_certfile
    
    # Legacy properties for backward compatibility
    @property
    def smtp_server(self) -> str:
        return self.email_settings.smtp_server
    
    @property
    def smtp_port(self) -> int:
        return self.email_settings.smtp_port
    
    @property
    def smtp_username(self) -> str:
        return self.email_settings.smtp_username
    
    @property
    def smtp_password(self) -> str:
        return self.email_settings.smtp_password
    
    @property
    def smtp_use_tls(self) -> bool:
        return self.email_settings.use_ssl
    
    @property
    def from_email(self) -> str:
        return self.email_settings.from_email
    
    @property
    def from_name(self) -> str:
        return self.email_settings.from_name
    
    @property
    def admin_email(self) -> str:
        return self.email_settings.company_email
    
    @property
    def azure_storage_connection_string(self) -> Optional[str]:
        return self.blob_storage_settings.connection_string
    
    @property
    def azure_storage_container_name(self) -> str:
        return self.blob_storage_settings.container_name
    
    # MFA settings (using application_settings for token config)
    @property
    def mfa_token_length(self) -> int:
        return self.application_settings.token_length
    
    @property
    def mfa_token_expiry_minutes(self) -> int:
        return self.application_settings.token_expiration_minutes
    
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
    
    def audit_configuration(self, logger=None) -> Dict[str, Any]:
        """
        Audit configuration loading and log which values are set for email settings.
        Returns a dictionary with configuration audit information.
        """
        import logging as log
        if logger is None:
            logger = log.getLogger(__name__)
        
        audit_info = {
            "config_source": "config.json",
            "email_config": {},
            "missing_fields": [],
            "warnings": []
        }
        
        logger.info(f"=== Configuration Audit ===")
        logger.info(f"Configuration source: config.json file")
        logger.info(f"Environment: {self.environment}")
        
        # Audit email configuration
        email_cfg = audit_info["email_config"]
        
        # Log email configuration values (non-secrets)
        logger.info(f"Email configuration values:")
        logger.info(f"  SMTP Server: {self.email_settings.smtp_server}")
        logger.info(f"  SMTP Port: {self.email_settings.smtp_port}")
        logger.info(f"  SMTP Username: {self.email_settings.smtp_username or '[NOT SET]'}")
        logger.info(f"  SMTP Password: {'[SET]' if self.email_settings.smtp_password else '[NOT SET]'}")
        logger.info(f"  From Email: {self.email_settings.from_email or '[NOT SET]'}")
        logger.info(f"  From Name: {self.email_settings.from_name}")
        logger.info(f"  Company Email: {self.email_settings.company_email or '[NOT SET]'}")
        logger.info(f"  Use SSL: {self.email_settings.use_ssl}")
        
        # Check for missing required fields and provide guidance
        required_fields = [
            ("smtp_username", "SmtpUsername", "your-email@gmail.com"),
            ("smtp_password", "SmtpPassword", "your-gmail-app-password"),
            ("from_email", "FromEmail", "noreply@yourdomain.com"),
            ("company_email", "CompanyEmail", "admin@yourdomain.com")
        ]
        
        for field_name, config_key, example in required_fields:
            field_value = getattr(self.email_settings, field_name)
            if not field_value:
                missing_info = {
                    "field": field_name,
                    "config_key": config_key,
                    "example": example
                }
                audit_info["missing_fields"].append(missing_info)
                logger.warning(f"Missing required email field: {field_name}")
                logger.warning(f"  Set in config.json: EmailSettings.{config_key}")
                logger.warning(f"  Example value: {example}")
        
        # Check for configuration warnings
        if not self.email_settings.smtp_username and not self.email_settings.smtp_password:
            warning = "Email service not configured - no SMTP credentials provided"
            audit_info["warnings"].append(warning)
            logger.warning(warning)
        elif not self.email_settings.smtp_username:
            warning = "SMTP username missing - email sending will fail"
            audit_info["warnings"].append(warning)
            logger.warning(warning)
        elif not self.email_settings.smtp_password:
            warning = "SMTP password missing - email sending will fail"  
            audit_info["warnings"].append(warning)
            logger.warning(warning)
            
        if not self.email_settings.from_email:
            warning = "From email address not configured - will use SMTP username as fallback"
            audit_info["warnings"].append(warning)
            logger.warning(warning)
            
        logger.info(f"=== End Configuration Audit ===")
        
        return audit_info


def load_config_from_file(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file '{config_path}' not found. "
            f"Please create it by copying from config.example.json and updating with your values."
        )
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file '{config_path}': {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration file '{config_path}': {e}")


def create_settings_from_config(config_data: Dict[str, Any]) -> Settings:
    """Create Settings object from config data"""
    
    # Logging settings
    logging_data = config_data.get("Logging", {})
    log_level_data = logging_data.get("LogLevel", {})
    console_data = logging_data.get("Console", {})
    
    logging_settings = LoggingSettings(
        default_level=LogLevel(log_level_data.get("Default", "Information")),
        microsoft_level=LogLevel(log_level_data.get("Microsoft", "Warning")),
        microsoft_hosting_lifetime_level=LogLevel(log_level_data.get("Microsoft.Hosting.Lifetime", "Information")),
        console_include_scopes=console_data.get("IncludeScopes", False),
        console_timestamp_format=console_data.get("TimestampFormat", "HH:mm:ss ")
    )
    
    # Email settings
    email_data = config_data.get("EmailSettings", {})
    email_settings = EmailSettings(
        smtp_server=email_data.get("SmtpServer", "smtp.gmail.com"),
        smtp_port=email_data.get("SmtpPort", 587),
        smtp_username=email_data.get("SmtpUsername", ""),
        smtp_password=email_data.get("SmtpPassword", ""),
        use_ssl=email_data.get("UseSsl", True),
        from_email=email_data.get("FromEmail", ""),
        from_name=email_data.get("FromName", "Azure Accommodation Form"),
        company_email=email_data.get("CompanyEmail", "")
    )
    
    # Blob storage settings
    blob_data = config_data.get("BlobStorageSettings", {})
    blob_storage_settings = BlobStorageSettings(
        connection_string=blob_data.get("ConnectionString") or None,
        container_name=blob_data.get("ContainerName", "form-submissions")
    )
    
    # Application settings
    app_data = config_data.get("ApplicationSettings", {})
    application_settings = ApplicationSettings(
        application_name=app_data.get("ApplicationName", "Azure Accommodation Form"),
        application_url=app_data.get("ApplicationUrl", "http://localhost:8000"),
        token_expiration_minutes=app_data.get("TokenExpirationMinutes", 15),
        token_length=app_data.get("TokenLength", 6)
    )
    
    # Application Insights settings
    insights_data = config_data.get("ApplicationInsights", {})
    application_insights = ApplicationInsightsSettings(
        connection_string=insights_data.get("ConnectionString") or None,
        agent_extension_version=insights_data.get("AgentExtensionVersion", "~2"),
        xdt_mode=insights_data.get("XdtMode", "default")
    )
    
    # Diagnostics settings
    diag_data = config_data.get("Diagnostics", {})
    website_data = config_data.get("Website", {})
    diagnostics = DiagnosticsSettings(
        azure_blob_retention_days=diag_data.get("AzureBlobRetentionInDays", 2),
        http_logging_retention_days=website_data.get("HttpLoggingRetentionDays", 2)
    )
    
    # Website settings
    web_data = config_data.get("Website", {})
    website = WebsiteSettings(
        http_logging_retention_days=web_data.get("HttpLoggingRetentionDays", 2)
    )
    
    # Server settings
    server_data = config_data.get("ServerSettings", {})
    server_settings = ServerSettings(
        environment=server_data.get("Environment", "development"),
        secret_key=server_data.get("SecretKey", "your-secret-key-change-in-production"),
        host=server_data.get("Host", "0.0.0.0"),
        port=server_data.get("Port", 8000),
        allowed_hosts=server_data.get("AllowedHosts", ["localhost", "127.0.0.1"]),
        allowed_origins=server_data.get("AllowedOrigins", ["http://localhost:8000", "http://127.0.0.1:8000"]),
        ssl_keyfile=server_data.get("SslKeyfile"),
        ssl_certfile=server_data.get("SslCertfile")
    )
    
    return Settings(
        logging=logging_settings,
        email_settings=email_settings,
        blob_storage_settings=blob_storage_settings,
        application_settings=application_settings,
        application_insights=application_insights,
        diagnostics=diagnostics,
        website=website,
        server_settings=server_settings
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance loaded from config.json"""
    config_data = load_config_from_file()
    
    # Validate email configuration
    email_data = config_data.get("EmailSettings", {})
    required_email_fields = ["SmtpUsername", "SmtpPassword", "FromEmail", "CompanyEmail"]
    missing_fields = [field for field in required_email_fields if not email_data.get(field)]
    
    if missing_fields:
        raise ValueError(
            f"Missing required email configuration fields in config.json: {', '.join(missing_fields)}. "
            f"Please update your config.json file with the required EmailSettings values."
        )
    
    return create_settings_from_config(config_data)