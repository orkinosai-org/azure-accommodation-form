"""
Basic tests for the Azure Accommodation Form application
"""

import pytest
from app.core.config import get_settings

def test_config_loading():
    """Test that configuration loads properly"""
    settings = get_settings()
    assert settings.app_name == "Azure Accommodation Form"
    assert isinstance(settings.port, int)

def test_environment_variables():
    """Test that environment variables are accessible"""
    import os
    # Test that we can load environment variables
    environment = os.getenv("ENVIRONMENT", "development")
    assert environment in ["development", "production", "testing"]

if __name__ == "__main__":
    pytest.main([__file__])