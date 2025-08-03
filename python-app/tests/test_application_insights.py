"""
Tests for Application Insights service
"""

import pytest
from unittest.mock import Mock, patch
from app.services.application_insights import ApplicationInsightsService, get_insights_service

def test_application_insights_service_init():
    """Test that Application Insights service initializes properly"""
    service = ApplicationInsightsService()
    
    # Test basic properties are set
    assert hasattr(service, 'connection_string')
    assert hasattr(service, 'agent_extension_version')
    assert hasattr(service, 'xdt_mode')
    assert hasattr(service, 'telemetry_client')

def test_track_event_without_telemetry():
    """Test event tracking when telemetry is not configured"""
    service = ApplicationInsightsService()
    
    # Should not raise an exception
    service.track_event("test_event", {"key": "value"})

def test_track_exception_without_telemetry():
    """Test exception tracking when telemetry is not configured"""
    service = ApplicationInsightsService()
    
    # Should not raise an exception
    test_exception = Exception("Test exception")
    service.track_exception(test_exception, {"key": "value"})

def test_track_dependency_without_telemetry():
    """Test dependency tracking when telemetry is not configured"""
    service = ApplicationInsightsService()
    
    # Should not raise an exception
    service.track_dependency("test_dependency", "test_data", 100.0, True)

def test_track_request_without_telemetry():
    """Test request tracking when telemetry is not configured"""
    service = ApplicationInsightsService()
    
    # Should not raise an exception
    service.track_request("test_request", "http://localhost", 200.0, 200, True)

def test_flush_without_telemetry():
    """Test flush when telemetry is not configured"""
    service = ApplicationInsightsService()
    
    # Should not raise an exception
    service.flush()

def test_get_insights_service_singleton():
    """Test that get_insights_service returns the same instance"""
    service1 = get_insights_service()
    service2 = get_insights_service()
    
    assert service1 is service2

def test_service_with_mock_connection_string():
    """Test service initialization with connection string (using mock)"""
    from unittest.mock import Mock
    
    # Mock the settings
    mock_settings = Mock()
    mock_settings.application_insights.connection_string = 'test_connection_string'
    mock_settings.application_insights.agent_extension_version = '~2'
    mock_settings.application_insights.xdt_mode = 'default'
    
    # Create service with mocked settings
    with patch('app.services.application_insights.get_settings', return_value=mock_settings):
        service = ApplicationInsightsService()
        assert service.connection_string == 'test_connection_string'

if __name__ == "__main__":
    pytest.main([__file__])