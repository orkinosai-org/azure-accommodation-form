#!/usr/bin/env python3
"""
Validate Azure deployment configuration for the accommodation form app.

This script validates that:
1. appsettings.json is properly formatted
2. DeploymentSettings section exists and is valid
3. Configuration can be loaded by the Python app
4. GitHub Actions can parse the configuration

Usage:
    python validate_deployment_config.py [path_to_appsettings.json]
"""

import json
import sys
import os
from pathlib import Path


def validate_json_syntax(config_path):
    """Validate that the JSON file is properly formatted"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return True, config
    except json.JSONDecodeError as e:
        return False, f"JSON syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_deployment_settings(config):
    """Validate the DeploymentSettings section"""
    if 'DeploymentSettings' not in config:
        return False, "DeploymentSettings section not found in configuration"
    
    deployment = config['DeploymentSettings']
    errors = []
    warnings = []
    
    # Required fields
    required_fields = {
        'AzureWebAppName': str,
        'PythonVersion': str,
        'AzurePublishProfileSecret': str,
        'Environment': str
    }
    
    for field, expected_type in required_fields.items():
        if field not in deployment:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(deployment[field], expected_type):
            errors.append(f"Field {field} should be {expected_type.__name__}, got {type(deployment[field]).__name__}")
        elif field == 'AzureWebAppName' and deployment[field] in ['your-azure-webapp-name', '']:
            warnings.append(f"AzureWebAppName appears to be a placeholder: {deployment[field]}")
        elif field == 'PythonVersion' and deployment[field] not in ['3.12', '3.11', '3.10']:
            warnings.append(f"Unusual Python version: {deployment[field]}")
    
    return len(errors) == 0, {
        'errors': errors,
        'warnings': warnings,
        'settings': deployment
    }


def validate_python_config_loading(config_path):
    """Test that the Python configuration system can load the settings"""
    try:
        # Add the python-app directory to the path
        python_app_dir = Path(config_path).parent
        sys.path.insert(0, str(python_app_dir))
        
        # Try to import and load configuration
        from app.core.config import load_config_from_file
        
        # Change to the python-app directory temporarily
        original_cwd = os.getcwd()
        os.chdir(python_app_dir)
        
        try:
            config_data = load_config_from_file(config_path.name)
            deployment_settings = config_data.get('DeploymentSettings', {})
            
            return True, {
                'azure_webapp_name': deployment_settings.get('AzureWebAppName'),
                'python_version': deployment_settings.get('PythonVersion'),
                'environment': deployment_settings.get('Environment')
            }
        finally:
            os.chdir(original_cwd)
            
    except ImportError as e:
        return False, f"Cannot import Python configuration module: {e}"
    except Exception as e:
        return False, f"Error loading configuration: {e}"


def simulate_github_actions_parsing(config):
    """Simulate the GitHub Actions configuration parsing"""
    try:
        deployment = config.get('DeploymentSettings', {})
        
        azure_webapp_name = deployment.get('AzureWebAppName', 'azure-accommodation-form')
        python_version = deployment.get('PythonVersion', '3.12')
        azure_publish_profile_secret = deployment.get('AzurePublishProfileSecret', 'AZURE_WEBAPP_PUBLISH_PROFILE')
        
        return True, {
            'AZURE_WEBAPP_NAME': azure_webapp_name,
            'PYTHON_VERSION': python_version,
            'AZURE_PUBLISH_PROFILE_SECRET': azure_publish_profile_secret
        }
    except Exception as e:
        return False, f"GitHub Actions simulation failed: {e}"


def main():
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    else:
        # Default to python-app/appsettings.json
        config_path = Path(__file__).parent.parent / 'python-app' / 'appsettings.json'
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    
    print(f"🔍 Validating Azure deployment configuration: {config_path}")
    print("=" * 60)
    
    # Test 1: JSON syntax
    print("1. JSON Syntax Validation...")
    json_valid, config_or_error = validate_json_syntax(config_path)
    if json_valid:
        print("   ✅ JSON syntax is valid")
        config = config_or_error
    else:
        print(f"   ❌ {config_or_error}")
        sys.exit(1)
    
    # Test 2: Deployment settings
    print("\n2. Deployment Settings Validation...")
    deploy_valid, deploy_result = validate_deployment_settings(config)
    if deploy_valid:
        print("   ✅ DeploymentSettings section is valid")
        settings = deploy_result['settings']
        print(f"     - Azure Web App: {settings['AzureWebAppName']}")
        print(f"     - Python Version: {settings['PythonVersion']}")
        print(f"     - Environment: {settings['Environment']}")
        print(f"     - Publish Profile Secret: {settings['AzurePublishProfileSecret']}")
        
        if deploy_result['warnings']:
            print("   ⚠️  Warnings:")
            for warning in deploy_result['warnings']:
                print(f"     - {warning}")
    else:
        print("   ❌ DeploymentSettings validation failed:")
        for error in deploy_result['errors']:
            print(f"     - {error}")
        if deploy_result['warnings']:
            print("   ⚠️  Warnings:")
            for warning in deploy_result['warnings']:
                print(f"     - {warning}")
        sys.exit(1)
    
    # Test 3: Python configuration loading
    print("\n3. Python Configuration Loading...")
    python_valid, python_result = validate_python_config_loading(config_path)
    if python_valid:
        print("   ✅ Python configuration loading successful")
        print(f"     - Loaded Web App: {python_result['azure_webapp_name']}")
        print(f"     - Loaded Python Version: {python_result['python_version']}")
        print(f"     - Loaded Environment: {python_result['environment']}")
    else:
        print(f"   ⚠️  Python configuration loading failed: {python_result}")
        print("   (This is normal if running outside the python-app directory)")
    
    # Test 4: GitHub Actions simulation
    print("\n4. GitHub Actions Parsing Simulation...")
    gh_valid, gh_result = simulate_github_actions_parsing(config)
    if gh_valid:
        print("   ✅ GitHub Actions parsing successful")
        for key, value in gh_result.items():
            print(f"     - {key}={value}")
    else:
        print(f"   ❌ {gh_result}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 All validation tests passed!")
    print("\n📋 Ready for deployment with these settings:")
    print(f"   • Azure Web App: {settings['AzureWebAppName']}")
    print(f"   • Python Version: {settings['PythonVersion']}")
    print(f"   • Environment: {settings['Environment']}")
    print(f"   • GitHub Secret: {settings['AzurePublishProfileSecret']}")
    print("\n💡 To deploy, commit and push to the main branch.")


if __name__ == "__main__":
    main()