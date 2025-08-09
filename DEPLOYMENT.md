# Deployment Guide for Azure Accommodation Form

This guide provides step-by-step instructions for deploying the Azure Accommodation Form application to Azure Web App.

## Overview

The application is available in two implementations:
- **Blazor (.NET 8)** - Recommended server-side implementation
- **Python (FastAPI)** - Alternative implementation

Both provide identical functionality for processing accommodation application forms with PDF generation, email notifications, and Azure Blob Storage integration.

## Prerequisites

Before deployment, ensure you have:

1. **Azure Subscription** with appropriate permissions
2. **Azure CLI** installed and configured
3. **Deployment package** downloaded from GitHub Actions artifacts
4. **Email account** for SMTP notifications (Gmail, Outlook, etc.)

## Step 1: Download and Extract Deployment Package

1. Navigate to the GitHub repository's Actions tab
2. Find the latest "Build Deployment Package" workflow run
3. Download the `deployment-package-zip` artifact
4. Extract the ZIP file to a local directory

The package contains:
```
deployment_package/
├── blazor-app/              # .NET 8 Blazor application
├── python-app/              # Python FastAPI application  
├── README.md                # Package overview
└── DEPLOYMENT.md           # This file
```

## Step 2: Choose Implementation

### Option A: Blazor (.NET 8) - Recommended

**Advantages:**
- Server-side rendering for better performance
- Built-in validation with C# models
- Type-safe development
- Excellent Azure integration

**Requirements:**
- Azure Web App with .NET 8 runtime
- Windows or Linux hosting plan

### Option B: Python (FastAPI) - Alternative

**Advantages:**
- Python ecosystem flexibility
- Familiar for Python developers
- Fast API performance

**Requirements:**
- Azure Web App with Python 3.12 runtime
- Linux hosting plan

## Step 3: Create Azure Resources

### 3.1 Create Resource Group

```bash
az group create --name rg-accommodation-form --location "East US"
```

### 3.2 Create Storage Account

```bash
# Create storage account
az storage account create \
  --name yourstorageaccount \
  --resource-group rg-accommodation-form \
  --location "East US" \
  --sku Standard_LRS

# Get connection string
az storage account show-connection-string \
  --name yourstorageaccount \
  --resource-group rg-accommodation-form \
  --query connectionString --output tsv
```

### 3.3 Create Blob Container

```bash
az storage container create \
  --name form-submissions \
  --account-name yourstorageaccount \
  --public-access off
```

### 3.4 Create Azure Web App

#### For Blazor (.NET 8):
```bash
# Create App Service Plan
az appservice plan create \
  --name asp-accommodation-form \
  --resource-group rg-accommodation-form \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --plan asp-accommodation-form \
  --runtime "DOTNETCORE:8.0"
```

#### For Python (FastAPI):
```bash
# Create App Service Plan
az appservice plan create \
  --name asp-accommodation-form-py \
  --resource-group rg-accommodation-form \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name your-python-app-name \
  --resource-group rg-accommodation-form \
  --plan asp-accommodation-form-py \
  --runtime "PYTHON:3.12"
```

## Step 4: Configure Environment Variables

### 4.1 Blazor Application Configuration

Set the following environment variables in Azure Web App Configuration:

#### Storage Settings:
```
BlobStorageSettings__ConnectionString = [Your storage connection string]
BlobStorageSettings__ContainerName = form-submissions
```

#### Email Settings:
```
EmailSettings__SmtpServer = smtp.gmail.com
EmailSettings__SmtpPort = 587
EmailSettings__SmtpUsername = [Your email address]
EmailSettings__SmtpPassword = [Your app password]
EmailSettings__UseSsl = true
EmailSettings__FromEmail = noreply@yourdomain.com
EmailSettings__FromName = Azure Accommodation Form
EmailSettings__CompanyEmail = admin@yourdomain.com
```

#### Database Settings (Optional - for logging):
```
ConnectionStrings__DefaultConnection = [SQL Server connection string]
```

#### Using Azure CLI:
```bash
# Set storage connection string
az webapp config appsettings set \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --settings "BlobStorageSettings__ConnectionString=YOUR_CONNECTION_STRING"

# Set email settings
az webapp config appsettings set \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --settings "EmailSettings__SmtpServer=smtp.gmail.com" \
              "EmailSettings__SmtpPort=587" \
              "EmailSettings__SmtpUsername=YOUR_EMAIL" \
              "EmailSettings__SmtpPassword=YOUR_PASSWORD"
```

### 4.2 Python Application Configuration

Set the following environment variables for Python app:

```
AZURE_STORAGE_CONNECTION_STRING = [Your storage connection string]
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = [Your email address]
SMTP_PASSWORD = [Your app password]
FROM_EMAIL = noreply@yourdomain.com
COMPANY_EMAIL = admin@yourdomain.com
SECRET_KEY = [Generate a secure secret key]
DEBUG = False
ENVIRONMENT = production
```

## Step 5: Deploy Application

### 5.1 Deploy Blazor Application

#### Option 1: Azure CLI Deployment
```bash
# Navigate to blazor-app directory in deployment package
cd deployment_package/blazor-app

# Create deployment ZIP
zip -r deploy.zip . -x "*.template" "startup.sh"

# Deploy to Azure
az webapp deployment source config-zip \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --src deploy.zip
```

#### Option 2: Azure Portal Deployment
1. Go to Azure Portal → Your Web App → Deployment Center
2. Choose "Local Git" or "External Git" 
3. Upload the blazor-app folder contents
4. Configure deployment settings

### 5.2 Deploy Python Application

#### Option 1: Azure CLI Deployment
```bash
# Navigate to python-app directory
cd deployment_package/python-app

# Create deployment ZIP (excluding templates)
zip -r deploy.zip . -x "*.template" "__pycache__/*" "*.pyc"

# Deploy to Azure
az webapp deployment source config-zip \
  --name your-python-app-name \
  --resource-group rg-accommodation-form \
  --src deploy.zip
```

#### Option 2: GitHub Actions (if using repository)
1. Fork the repository
2. Set up Azure credentials in GitHub Secrets
3. Use existing workflows as reference

## Step 6: Configure Email Settings

### 6.1 Gmail Configuration

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App Passwords
   - Select "Mail" and generate password
3. **Use App Password** in `SmtpPassword` setting (not your regular password)

### 6.2 Outlook/Hotmail Configuration

```
SmtpServer: smtp-mail.outlook.com
SmtpPort: 587
UseSsl: true
```

### 6.3 Custom SMTP Configuration

Contact your email provider for SMTP settings and configure accordingly.

## Step 7: Verify Deployment

### 7.1 Check Application Status

```bash
# Check webapp status
az webapp show \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --query state
```

### 7.2 View Application Logs

```bash
# Enable logging
az webapp log config \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --web-server-logging filesystem

# View logs
az webapp log tail \
  --name your-app-name \
  --resource-group rg-accommodation-form
```

### 7.3 Test Application

1. **Navigate to your app URL**: `https://your-app-name.azurewebsites.net`
2. **Test form submission** with a sample entry
3. **Verify email delivery** (check inbox and spam folder)
4. **Check blob storage** for generated PDFs

## Step 8: Security Configuration

### 8.1 Enable HTTPS Only

```bash
az webapp update \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --https-only true
```

### 8.2 Configure Custom Domain (Optional)

```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name your-app-name \
  --resource-group rg-accommodation-form \
  --hostname yourdomain.com
```

### 8.3 Enable Application Insights (Recommended)

```bash
# Create Application Insights
az monitor app-insights component create \
  --app accommodation-form-insights \
  --location "East US" \
  --resource-group rg-accommodation-form

# Configure webapp to use insights
az webapp config appsettings set \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=YOUR_INSTRUMENTATION_KEY"
```

## Troubleshooting

### Common Issues

#### 1. Application Not Starting
- **Check logs**: Use `az webapp log tail` to view error messages
- **Verify runtime**: Ensure correct .NET/Python version is configured
- **Check startup command**: For Python apps, verify startup script

#### 2. Email Not Sending
- **Verify SMTP settings**: Double-check server, port, credentials
- **Check firewall**: Ensure Azure can reach SMTP server
- **Test credentials**: Use separate email client to verify settings

#### 3. File Upload Issues
- **Storage connection**: Verify blob storage connection string
- **Container permissions**: Ensure container exists and is accessible
- **File size limits**: Check Azure Web App file upload limits

#### 4. Performance Issues
- **Scale up**: Consider higher App Service Plan tier
- **Enable caching**: Configure appropriate caching strategies
- **Monitor metrics**: Use Application Insights for performance monitoring

### Debugging Commands

```bash
# Check environment variables
az webapp config appsettings list \
  --name your-app-name \
  --resource-group rg-accommodation-form

# Restart webapp
az webapp restart \
  --name your-app-name \
  --resource-group rg-accommodation-form

# Check deployment status
az webapp deployment list-publishing-profiles \
  --name your-app-name \
  --resource-group rg-accommodation-form
```

## Maintenance

### 8.1 Regular Updates

1. **Monitor security updates** for .NET/Python
2. **Update dependencies** regularly
3. **Review logs** for errors or performance issues
4. **Backup configuration** and important data

### 8.2 Backup Strategy

1. **Export app settings**: Regularly backup environment variables
2. **Database backups**: If using SQL Database, configure automated backups
3. **Blob storage**: Consider backup or replication for PDFs

### 8.3 Monitoring

1. **Set up alerts** for application errors
2. **Monitor performance** metrics
3. **Track usage** patterns
4. **Regular health checks**

## Support

### Getting Help

1. **Check logs first** using Azure CLI or portal
2. **Review this documentation** for common issues
3. **Azure Support**: For Azure-specific issues
4. **Application Issues**: Review application logs and error messages

### Useful Resources

- [Azure Web Apps Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [.NET on Azure Documentation](https://docs.microsoft.com/en-us/dotnet/azure/)
- [Python on Azure Documentation](https://docs.microsoft.com/en-us/azure/developer/python/)
- [Azure Blob Storage Documentation](https://docs.microsoft.com/en-us/azure/storage/blobs/)

---

## Quick Reference

### Blazor App URLs
- **Application**: `https://your-app-name.azurewebsites.net`
- **API Documentation**: `https://your-app-name.azurewebsites.net/swagger`
- **Health Check**: `https://your-app-name.azurewebsites.net/health`

### Python App URLs
- **Application**: `https://your-python-app-name.azurewebsites.net`
- **API Documentation**: `https://your-python-app-name.azurewebsites.net/docs`
- **Health Check**: `https://your-python-app-name.azurewebsites.net/health`

### Resource Naming Convention
```
Resource Group: rg-accommodation-form
Storage Account: yourstorageaccount
App Service Plan: asp-accommodation-form
Web App: your-app-name
Application Insights: accommodation-form-insights
```

This deployment guide provides comprehensive instructions for successfully deploying the Azure Accommodation Form application. Follow the steps carefully and refer to the troubleshooting section if you encounter any issues.