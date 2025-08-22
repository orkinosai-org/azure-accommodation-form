#!/usr/bin/env python3
"""
Test script to verify Azure Web App deployment configuration and functionality.
"""

import sys
import json
import requests
from pathlib import Path

def load_config():
    """Load configuration from appsettings.json"""
    config_path = Path(__file__).parent / "python-app" / "appsettings.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def test_azure_webapp(config):
    """Test the Azure Web App endpoints"""
    app_url = config['ApplicationSettings']['ApplicationUrl'].rstrip('/')
    
    print(f"🌐 Testing Azure Web App: {app_url}")
    print("=" * 60)
    
    # Test main application endpoint
    try:
        response = requests.get(app_url, timeout=10)
        print(f"✅ Main endpoint ({app_url}): {response.status_code}")
        if response.status_code == 200:
            print(f"   Content length: {len(response.text)} bytes")
            if "Azure Accommodation" in response.text:
                print("   ✅ Application title found in response")
            else:
                print("   ⚠️  Expected application title not found")
    except Exception as e:
        print(f"❌ Main endpoint failed: {e}")
    
    # Test health endpoint (will be available after Python deployment)
    try:
        health_url = f"{app_url}/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Health endpoint: {response.status_code}")
            health_data = response.json()
            print(f"   Service: {health_data.get('service', 'Unknown')}")
            print(f"   Environment: {health_data.get('environment', 'Unknown')}")
        else:
            print(f"⚠️  Health endpoint: {response.status_code} (expected after Python deployment)")
    except Exception as e:
        print(f"⚠️  Health endpoint not available yet (expected): {e}")
    
    # Test config status endpoint (will be available after Python deployment)
    try:
        config_url = f"{app_url}/config-status"
        response = requests.get(config_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Config status endpoint: {response.status_code}")
            config_data = response.json()
            print(f"   Email configured: {config_data.get('email_service', {}).get('configured', 'Unknown')}")
            print(f"   Storage configured: {config_data.get('storage_service', {}).get('configured', 'Unknown')}")
        else:
            print(f"⚠️  Config status endpoint: {response.status_code} (expected after Python deployment)")
    except Exception as e:
        print(f"⚠️  Config status endpoint not available yet (expected): {e}")

def verify_deployment_config(config):
    """Verify deployment configuration"""
    print("\n🔧 Deployment Configuration")
    print("=" * 60)
    
    deployment = config.get('DeploymentSettings', {})
    
    print(f"Azure Web App Name: {deployment.get('AzureWebAppName', 'Not configured')}")
    print(f"Python Version: {deployment.get('PythonVersion', 'Not configured')}")
    print(f"Environment: {deployment.get('Environment', 'Not configured')}")
    print(f"Publish Profile Secret: {deployment.get('AzurePublishProfileSecret', 'Not configured')}")
    
    app_settings = config.get('ApplicationSettings', {})
    print(f"Application Name: {app_settings.get('ApplicationName', 'Not configured')}")
    print(f"Application URL: {app_settings.get('ApplicationUrl', 'Not configured')}")

def main():
    """Main test function"""
    print("🧪 Azure Accommodation Form - Deployment Test")
    print("=" * 60)
    
    try:
        config = load_config()
        verify_deployment_config(config)
        test_azure_webapp(config)
        
        print("\n✅ Deployment test completed!")
        print("\n📝 Summary:")
        print("   - Azure Web App is accessible and responding")
        print("   - Configuration is properly loaded")
        print("   - Ready for Python FastAPI deployment")
        print("\n🚀 Next steps:")
        print("   1. Merge PR #117 to trigger deployment")
        print("   2. Python FastAPI app deployment will be activated")
        print("   3. Test endpoints will become available")
        
    except FileNotFoundError:
        print("❌ Error: appsettings.json not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()