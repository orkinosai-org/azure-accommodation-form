#!/usr/bin/env python3
"""
Azure Accommodation Form - Deployment Package Builder

This script creates a clean deployment package with safe configuration files
that clients can easily edit before or after deployment.
"""

import os
import shutil
import subprocess
import zipfile
import json
import tempfile
from pathlib import Path
import sys

def print_step(step, message):
    """Print a formatted step message."""
    print(f"\n🔧 Step {step}: {message}")
    print("=" * (len(message) + 20))

def run_command(command, cwd=None, description=None):
    """Run a command and handle errors."""
    if description:
        print(f"   Running: {description}")
    
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        raise

def clean_directory(path):
    """Remove directory if it exists."""
    if os.path.exists(path):
        print(f"   Cleaning existing directory: {path}")
        shutil.rmtree(path)

def copy_with_exclusions(src, dst, exclude_patterns=None):
    """Copy directory with exclusions."""
    if exclude_patterns is None:
        exclude_patterns = []
    
    def should_exclude(path):
        path_str = str(path)
        for pattern in exclude_patterns:
            if pattern in path_str:
                return True
        return False
    
    for root, dirs, files in os.walk(src):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
        
        # Create destination directory
        rel_path = os.path.relpath(root, src)
        if rel_path == '.':
            dst_dir = dst
        else:
            dst_dir = os.path.join(dst, rel_path)
        
        if not should_exclude(root):
            os.makedirs(dst_dir, exist_ok=True)
            
            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                if not should_exclude(src_file):
                    dst_file = os.path.join(dst_dir, file)
                    shutil.copy2(src_file, dst_file)

def sanitize_config_files(directory):
    """Remove any remaining real credentials from documentation files."""
    print("   Sanitizing configuration files...")
    
    # List of real values to replace
    replacements = {
        "ismailkucukdurgut@gmail.com": "YOUR_EMAIL@gmail.com",
        "ftin cwaw jiii fwar": "YOUR_APP_PASSWORD",
        "accofornstorageaccount": "YOUR_STORAGE_ACCOUNT_NAME",
        "MTJf54NM7TEcpGTVRaokyTU+6Uy08H8OubuMOrwOhAy2K3hbNbQLvKpyHI/Iq/0p28NnJwtn/gTv+AStsL0GEg==": "YOUR_STORAGE_ACCOUNT_KEY"
    }
    
    # Process all markdown and text files
    for file_path in directory.rglob('*.md'):
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            for real_value, placeholder in replacements.items():
                content = content.replace(real_value, placeholder)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"      Sanitized: {file_path.relative_to(directory)}")
        except Exception as e:
            print(f"      Warning: Could not sanitize {file_path}: {e}")

def create_safe_appsettings(template_path, output_path):
    """Create appsettings.json with safe placeholder values."""
    print(f"   Creating safe appsettings.json: {output_path}")
    
    # Use our pre-created safe template
    safe_config_path = os.path.join(os.path.dirname(__file__), 'appsettings.deployment.json')
    if os.path.exists(safe_config_path):
        shutil.copy2(safe_config_path, output_path)
        print(f"   ✅ Safe configuration copied from template")
    else:
        print(f"   ⚠️  Template not found, creating basic safe config")
        # Fallback: create basic safe config
        safe_config = {
            "Logging": {
                "LogLevel": {
                    "Default": "Information",
                    "Microsoft": "Warning",
                    "Microsoft.Hosting.Lifetime": "Information"
                }
            },
            "AllowedHosts": "*",
            "ConnectionStrings": {
                "DefaultConnection": "Server=YOUR_SQL_SERVER_NAME.database.windows.net;Database=YOUR_DATABASE_NAME;User Id=YOUR_DATABASE_USERNAME;Password=YOUR_DATABASE_PASSWORD;Encrypt=True;TrustServerCertificate=False;"
            },
            "EmailSettings": {
                "SmtpServer": "smtp.gmail.com",
                "SmtpPort": 587,
                "SmtpUsername": "YOUR_EMAIL@gmail.com",
                "SmtpPassword": "YOUR_APP_PASSWORD",
                "UseSsl": True,
                "FromEmail": "noreply@yourdomain.com",
                "FromName": "Azure Accommodation Form",
                "CompanyEmail": "admin@yourdomain.com"
            },
            "BlobStorageSettings": {
                "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=YOUR_STORAGE_ACCOUNT_NAME;AccountKey=YOUR_STORAGE_ACCOUNT_KEY;EndpointSuffix=core.windows.net",
                "ContainerName": "form-submissions"
            },
            "ApplicationSettings": {
                "ApplicationName": "Azure Accommodation Form",
                "ApplicationUrl": "https://YOUR_APP_NAME.azurewebsites.net",
                "TokenExpirationMinutes": 15,
                "TokenLength": 6
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(safe_config, f, indent=2)

def main():
    """Main function to create deployment package."""
    print("🚀 Azure Accommodation Form - Deployment Package Builder")
    print("=" * 60)
    
    # Setup paths
    script_dir = Path(__file__).parent
    repo_root = script_dir
    deployment_dir = repo_root / "deployment_package"
    temp_build_dir = repo_root / "temp_build"
    
    try:
        # Step 1: Clean previous builds
        print_step(1, "Cleaning previous builds")
        clean_directory(deployment_dir)
        clean_directory(temp_build_dir)
        
        # Step 2: Create deployment structure
        print_step(2, "Creating deployment package structure")
        deployment_dir.mkdir(exist_ok=True)
        
        # Step 3: Build Blazor application
        print_step(3, "Building Blazor application for production")
        blazor_app_dir = repo_root / "BlazorApp"
        blazor_output_dir = deployment_dir / "blazor-app"
        
        if blazor_app_dir.exists():
            print("   Building .NET application...")
            run_command("dotnet restore", cwd=blazor_app_dir, description="Restoring NuGet packages")
            run_command(f"dotnet publish --configuration Release --output {temp_build_dir / 'blazor'} --no-restore", 
                       cwd=blazor_app_dir, description="Publishing Blazor app")
            
            # Copy built application
            print("   Copying Blazor application to deployment package...")
            shutil.copytree(temp_build_dir / 'blazor', blazor_output_dir)
            
            # Create safe appsettings.json
            create_safe_appsettings(
                blazor_app_dir / "appsettings.json",
                blazor_output_dir / "appsettings.json"
            )
            
            print("   ✅ Blazor application prepared")
        else:
            print("   ⚠️  BlazorApp directory not found, skipping Blazor build")
        
        # Step 4: Prepare Python application
        print_step(4, "Preparing Python application")
        python_app_dir = repo_root / "python-app"
        python_output_dir = deployment_dir / "python-app"
        
        if python_app_dir.exists():
            print("   Copying Python application...")
            exclude_patterns = [
                "__pycache__",
                ".pyc",
                "venv",
                ".venv",
                ".env",
                "test_",
                ".pytest_cache",
                "appsettings.json.backup",
                "appsettings_test.json",
                "GMAIL_SMTP_CONFIGURATION.md",  # Contains real credentials
                "APPSETTINGS_JSON_GUIDE.md",    # May contain real examples
                "AZURE_DEPLOYMENT_CONFIG.md"    # May contain real examples
            ]
            
            copy_with_exclusions(python_app_dir, python_output_dir, exclude_patterns)
            
            # Create safe appsettings.json for Python
            python_safe_config = {
                "azure_storage_connection_string": "DefaultEndpointsProtocol=https;AccountName=YOUR_STORAGE_ACCOUNT_NAME;AccountKey=YOUR_STORAGE_ACCOUNT_KEY;EndpointSuffix=core.windows.net",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "YOUR_EMAIL@gmail.com",
                "smtp_password": "YOUR_APP_PASSWORD",
                "from_email": "noreply@yourdomain.com",
                "company_email": "admin@yourdomain.com",
                "secret_key": "your-secret-key-here-change-this",
                "debug": False,
                "environment": "production"
            }
            
            with open(python_output_dir / "appsettings.json", 'w') as f:
                json.dump(python_safe_config, f, indent=2)
            
            # Sanitize any remaining files with real credentials
            sanitize_config_files(python_output_dir)
            
            print("   ✅ Python application prepared")
        else:
            print("   ⚠️  python-app directory not found, skipping Python preparation")
        
        # Step 5: Copy deployment documentation
        print_step(5, "Adding deployment documentation")
        
        # Copy our client-friendly deployment guide
        deployment_guide_path = repo_root / "DEPLOYMENT_PACKAGE.md"
        if deployment_guide_path.exists():
            shutil.copy2(deployment_guide_path, deployment_dir / "DEPLOYMENT.md")
            print("   ✅ Client-friendly deployment guide added")
        else:
            print("   ⚠️  DEPLOYMENT_PACKAGE.md not found, using basic instructions")
            with open(deployment_dir / "DEPLOYMENT.md", 'w') as f:
                f.write("""# Deployment Instructions

1. Edit appsettings.json with your actual configuration values
2. Deploy to Azure Web App
3. Test your application

See the original DEPLOYMENT.md for detailed instructions.
""")
        
        # Create README for the package
        with open(deployment_dir / "README.md", 'w') as f:
            f.write("""# Azure Accommodation Form - Deployment Package

This package contains everything you need to deploy the Azure Accommodation Form.

## Quick Start
1. Edit `appsettings.json` in the blazor-app or python-app folder
2. Replace placeholder values with your real configuration
3. Deploy to Azure Web App
4. See DEPLOYMENT.md for detailed instructions

## Package Contents
- `blazor-app/` - .NET 8 Blazor application (recommended)
- `python-app/` - Python FastAPI application (alternative)
- `DEPLOYMENT.md` - Detailed deployment instructions
- `README.md` - This file

Choose either the Blazor or Python implementation based on your preference.
""")
        
        # Step 6: Clean up temporary files
        print_step(6, "Cleaning up temporary files")
        clean_directory(temp_build_dir)
        
        # Step 7: Create ZIP file
        print_step(7, "Creating deployment package ZIP")
        zip_path = repo_root / "deployment_package.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(deployment_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, deployment_dir)
                    zipf.write(file_path, arc_path)
        
        # Step 8: Generate summary
        print_step(8, "Deployment Package Summary")
        
        # Calculate sizes
        package_size = sum(f.stat().st_size for f in deployment_dir.rglob('*') if f.is_file())
        zip_size = zip_path.stat().st_size
        
        print(f"   📦 Package directory: {deployment_dir}")
        print(f"   📦 ZIP file: {zip_path}")
        print(f"   📊 Package size: {package_size / 1024 / 1024:.1f} MB")
        print(f"   📊 ZIP size: {zip_size / 1024 / 1024:.1f} MB")
        
        # List contents
        print("\n   📋 Package contents:")
        for item in sorted(deployment_dir.rglob('*')):
            if item.is_file():
                rel_path = item.relative_to(deployment_dir)
                size = item.stat().st_size
                print(f"      {rel_path} ({size / 1024:.1f} KB)")
        
        print("\n🎉 Deployment package created successfully!")
        print("=" * 50)
        print(f"✅ Ready-to-deploy package: {zip_path}")
        print("✅ Safe configuration files with placeholders")
        print("✅ Client-friendly documentation included")
        print("✅ All sensitive data removed")
        print("\nNext steps:")
        print("1. Extract deployment_package.zip")
        print("2. Edit appsettings.json with real values")
        print("3. Deploy to Azure Web App")
        print("4. Test your application")
        
    except Exception as e:
        print(f"\n❌ Error creating deployment package: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()