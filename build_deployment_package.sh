#!/bin/bash

# Azure Accommodation Form - Deployment Package Creator
# This script creates a safe deployment package for client distribution

echo "🚀 Azure Accommodation Form - Deployment Package Creator"
echo "========================================================"
echo ""
echo "This script will create a deployment package with:"
echo "✅ Ready-to-deploy application files"
echo "✅ Safe configuration templates (no real secrets)"
echo "✅ Client-friendly documentation"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if .NET is available
if ! command -v dotnet &> /dev/null; then
    echo "❌ Error: .NET SDK is required but not installed."
    echo "Please install .NET 8 SDK and try again."
    exit 1
fi

echo "Prerequisites check passed ✅"
echo ""

# Ask for confirmation
read -p "Do you want to create the deployment package? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Creating deployment package..."
    python3 create_deployment_package.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Deployment package created successfully!"
        echo ""
        echo "📦 Package: deployment_package.zip"
        echo "📋 Instructions:"
        echo "   1. Send deployment_package.zip to your client"
        echo "   2. Client extracts the ZIP file"
        echo "   3. Client edits appsettings.json with their real values"
        echo "   4. Client deploys to Azure Web App"
        echo ""
        echo "The package contains NO real secrets - only safe placeholders."
    else
        echo ""
        echo "❌ Error: Failed to create deployment package."
        echo "Please check the error messages above and try again."
        exit 1
    fi
else
    echo "Operation cancelled."
    exit 0
fi