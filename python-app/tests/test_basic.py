"""
Basic tests for the Azure Accommodation Form application
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_page():
    """Test the root page loads"""
    response = client.get("/")
    assert response.status_code == 200

def test_certificate_verification():
    """Test certificate verification endpoint"""
    response = client.post("/api/auth/verify-certificate")
    # In development mode, this should pass
    assert response.status_code in [200, 401]  # Depends on certificate presence

if __name__ == "__main__":
    pytest.main([__file__])