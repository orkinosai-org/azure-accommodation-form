"""
Application Insights service for telemetry and monitoring

This service provides Application Insights integration that mirrors the .NET
ApplicationInsights configuration from appsettings.json.
"""

import logging
from typing import Optional, Dict, Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class ApplicationInsightsService:
    """
    Service for Application Insights integration
    
    This service mirrors the .NET ApplicationInsights configuration and provides
    Python equivalents for telemetry tracking.
    """
    
    def __init__(self):
        settings = get_settings()
        self.insights_settings = settings.application_insights
        
        self.connection_string = self.insights_settings.connection_string
        self.agent_extension_version = self.insights_settings.agent_extension_version
        self.xdt_mode = self.insights_settings.xdt_mode
        
        self.telemetry_client = None
        self._initialize_telemetry()
    
    def _initialize_telemetry(self):
        """Initialize Application Insights telemetry if configured"""
        if not self.connection_string:
            logger.info("Application Insights not configured - telemetry disabled")
            return
        
        try:
            # Try to initialize Application Insights using opencensus
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            from opencensus.ext.azure.trace_exporter import AzureExporter
            from opencensus.trace.samplers import ProbabilitySampler
            from opencensus.trace.tracer import Tracer
            
            # Configure logging handler
            azure_log_handler = AzureLogHandler(
                connection_string=self.connection_string
            )
            
            # Add custom properties that mirror .NET configuration
            azure_log_handler.add_telemetry_processor(self._add_custom_properties)
            
            # Add handler to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(azure_log_handler)
            
            # Configure trace exporter
            tracer = Tracer(
                exporter=AzureExporter(connection_string=self.connection_string),
                sampler=ProbabilitySampler(1.0)
            )
            
            self.telemetry_client = {
                'log_handler': azure_log_handler,
                'tracer': tracer
            }
            
            logger.info("Application Insights telemetry initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Application Insights libraries not available: {e}")
            logger.info("To enable Application Insights, install: pip install opencensus-ext-azure")
        except Exception as e:
            logger.error(f"Failed to initialize Application Insights: {e}")
    
    def _add_custom_properties(self, envelope):
        """Add custom properties that mirror .NET Application Insights configuration"""
        envelope.tags['ai.cloud.roleInstance'] = f"python-app-{self.xdt_mode}"
        envelope.tags['ai.internal.sdkVersion'] = f"py{self.agent_extension_version}"
        return True
    
    def track_event(self, name: str, properties: Optional[Dict[str, Any]] = None):
        """Track a custom event (similar to .NET TrackEvent)"""
        try:
            if self.telemetry_client:
                logger.info(f"Event tracked: {name}", extra={'custom_dimensions': properties or {}})
            else:
                logger.info(f"Event (no telemetry): {name} - {properties}")
        except Exception as e:
            logger.error(f"Failed to track event {name}: {e}")
    
    def track_exception(self, exception: Exception, properties: Optional[Dict[str, Any]] = None):
        """Track an exception (similar to .NET TrackException)"""
        try:
            if self.telemetry_client:
                logger.exception(f"Exception tracked: {exception}", extra={'custom_dimensions': properties or {}})
            else:
                logger.exception(f"Exception (no telemetry): {exception}")
        except Exception as e:
            logger.error(f"Failed to track exception: {e}")
    
    def track_dependency(self, name: str, data: str, duration: float, success: bool = True):
        """Track a dependency call (similar to .NET TrackDependency)"""
        try:
            if self.telemetry_client:
                properties = {
                    'dependency_name': name,
                    'dependency_data': data,
                    'duration_ms': duration,
                    'success': success
                }
                logger.info(f"Dependency tracked: {name}", extra={'custom_dimensions': properties})
            else:
                logger.info(f"Dependency (no telemetry): {name} - {data} - {duration}ms - Success: {success}")
        except Exception as e:
            logger.error(f"Failed to track dependency {name}: {e}")
    
    def track_request(self, name: str, url: str, duration: float, response_code: int, success: bool = True):
        """Track an HTTP request (similar to .NET TrackRequest)"""
        try:
            if self.telemetry_client:
                properties = {
                    'request_name': name,
                    'request_url': url,
                    'duration_ms': duration,
                    'response_code': response_code,
                    'success': success
                }
                logger.info(f"Request tracked: {name}", extra={'custom_dimensions': properties})
            else:
                logger.info(f"Request (no telemetry): {name} - {url} - {response_code} - {duration}ms")
        except Exception as e:
            logger.error(f"Failed to track request {name}: {e}")
    
    def flush(self):
        """Flush telemetry data (similar to .NET Flush)"""
        try:
            if self.telemetry_client:
                # Note: opencensus handles flushing automatically
                logger.debug("Telemetry data flushed")
        except Exception as e:
            logger.error(f"Failed to flush telemetry: {e}")

# Global instance for easy access
_insights_service = None

def get_insights_service() -> ApplicationInsightsService:
    """Get or create the global Application Insights service instance"""
    global _insights_service
    if _insights_service is None:
        _insights_service = ApplicationInsightsService()
    return _insights_service