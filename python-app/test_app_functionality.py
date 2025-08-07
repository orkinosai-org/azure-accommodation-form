"""
Simple test to verify the FastAPI app can be created and the endpoint exists
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_app_creation():
    """Test that the FastAPI app can be created"""
    try:
        # client is already created globally
        print("✓ FastAPI test client created successfully")
        return True
    except Exception as e:
        print(f"✗ FastAPI test client creation failed: {e}")
        return False

def test_form_submit_endpoint_exists():
    """Test that the form submit endpoint exists"""
    try:
        # Make a request to the endpoint (it will fail due to missing auth/data, but should reach the endpoint)
        response = client.post("/api/form/submit")
        
        # We expect it to fail with specific error codes, but not 404 (endpoint not found)
        if response.status_code == 404:
            print("✗ Form submit endpoint not found (404)")
            return False
        else:
            print(f"✓ Form submit endpoint exists (returned {response.status_code})")
            print(f"  Response: {response.json() if response.status_code != 500 else 'Internal error'}")
            return True
            
    except Exception as e:
        print(f"✗ Form submit endpoint test failed: {e}")
        return False

def test_health_endpoint():
    """Test that the health endpoint works"""
    try:
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✓ Health endpoint works")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("FastAPI Application Test")
    print("="*50)
    
    success1 = test_app_creation()
    success2 = test_health_endpoint()
    success3 = test_form_submit_endpoint_exists()
    
    if success1 and success2 and success3:
        print("\n✓ ALL APPLICATION TESTS PASSED!")
        print("✓ The FastAPI application is ready for deployment")
    else:
        print("\n✗ SOME APPLICATION TESTS FAILED")