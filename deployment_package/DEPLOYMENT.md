# Azure Web App Deployment Guide - Python FastAPI Application

This deployment package contains a production-ready Python FastAPI web application for processing accommodation forms with PDF generation, email notifications, and Azure Blob Storage integration.

## Package Contents

This ZIP deployment package includes:
- **Python FastAPI Application** (`app/` directory) - Complete web application
- **Main Entry Point** (`main.py`) - FastAPI application startup
- **Dependencies** (`requirements.txt`) - Python package requirements
- **Startup Script** (`startup.sh`) - Azure Web App startup script
- **Static Files** (`app/static/`) - CSS and JavaScript assets
- **Templates** (`app/templates/`) - HTML templates
- **Configuration Templates** (`.env.example`, `appsettings.example.json`) - Environment setup guides

## Prerequisites

Before deploying to Azure Web App, ensure you have:

1. **Azure Subscription** with Web App deployment permissions
2. **Azure CLI** installed and authenticated (`az login`)
3. **Email Account** for SMTP notifications (Gmail, Outlook, etc.)
4. **Azure Storage Account** for blob storage (optional)

## Step 1: Create Azure Web App

### 1.1 Create Resource Group
```bash
az group create --name rg-accommodation-form --location "East US"
```

### 1.2 Create Azure Web App Service Plan
```bash
az appservice plan create \
  --name asp-accommodation-form \
  --resource-group rg-accommodation-form \
  --location "East US" \
  --sku B1 \
  --is-linux
```

### 1.3 Create Web App with Python 3.12 Runtime
```bash
az webapp create \
  --name accommodation-form-app \
  --resource-group rg-accommodation-form \
  --plan asp-accommodation-form \
  --runtime "PYTHON:3.12"
```

## Step 2: Deploy Using ZIP Deploy Method

### 2.1 Deploy the ZIP Package
```bash
az webapp deploy \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app \
  --src-path ./deployment_package.zip \
  --type zip
```

### 2.2 Set Startup Command
Configure the startup command in Azure Portal or via CLI:
```bash
az webapp config set \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app \
  --startup-file "startup.sh"
```

## Step 3: Configure Environment Variables

### 3.1 Required Environment Variables
Set these in Azure Portal → App Service → Configuration → Application Settings:

#### Basic Application Settings
```
ENVIRONMENT=production
SECRET_KEY=your-secure-secret-key-make-it-long-and-random
PORT=8000
ALLOWED_HOSTS=your-app-name.azurewebsites.net,yourdomain.com
ALLOWED_ORIGINS=https://your-app-name.azurewebsites.net,https://yourdomain.com
```

#### Email Configuration (SMTP)
```
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-gmail-app-password
EMAIL_USE_SSL=true
EMAIL_FROM_EMAIL=your-email@gmail.com
EMAIL_FROM_NAME=Azure Accommodation Form
EMAIL_COMPANY_EMAIL=your-email@gmail.com
```

#### Azure Blob Storage (Optional)
```
BLOB_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=yourkey;EndpointSuffix=core.windows.net
BLOB_STORAGE_CONTAINER_NAME=form-submissions
```

#### Application Insights (Optional)
```
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/
```

### 3.2 Setting Environment Variables via Azure Portal

1. Navigate to **Azure Portal** → **App Services** → **Your App**
2. Go to **Configuration** → **Application settings**
3. Click **+ New application setting**
4. Add each environment variable from the list above
5. Click **Save** when done

### 3.3 Setting Environment Variables via Azure CLI
```bash
# Set basic application settings
az webapp config appsettings set \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app \
  --settings \
    ENVIRONMENT=production \
    SECRET_KEY="your-secure-secret-key-make-it-long-and-random" \
    PORT=8000 \
    ALLOWED_HOSTS="your-app-name.azurewebsites.net" \
    ALLOWED_ORIGINS="https://your-app-name.azurewebsites.net"

# Set email configuration
az webapp config appsettings set \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app \
  --settings \
    EMAIL_SMTP_SERVER="smtp.gmail.com" \
    EMAIL_SMTP_PORT=587 \
    EMAIL_SMTP_USERNAME="your-email@gmail.com" \
    EMAIL_SMTP_PASSWORD="your-gmail-app-password" \
    EMAIL_USE_SSL=true \
    EMAIL_FROM_EMAIL="your-email@gmail.com" \
    EMAIL_FROM_NAME="Azure Accommodation Form" \
    EMAIL_COMPANY_EMAIL="your-email@gmail.com"
```

## Step 4: Verify Deployment

### 4.1 Check Application Status
```bash
az webapp show \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app \
  --query "state"
```

### 4.2 View Application Logs
```bash
az webapp log tail \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app
```

### 4.3 Test Application
1. Open your browser to `https://your-app-name.azurewebsites.net`
2. Verify the accommodation form loads correctly
3. Test form submission (ensure email configuration is working)

## Step 5: Optional - Configure Custom Domain

### 5.1 Add Custom Domain
```bash
az webapp config hostname add \
  --resource-group rg-accommodation-form \
  --webapp-name accommodation-form-app \
  --hostname yourdomain.com
```

### 5.2 Enable HTTPS
```bash
az webapp config ssl bind \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app \
  --certificate-thumbprint your-cert-thumbprint \
  --ssl-type SNI
```

## Step 6: Optional - Set Up Azure Blob Storage

### 6.1 Create Storage Account
```bash
az storage account create \
  --name yourstorageaccount \
  --resource-group rg-accommodation-form \
  --location "East US" \
  --sku Standard_LRS
```

### 6.2 Create Blob Container
```bash
az storage container create \
  --name form-submissions \
  --account-name yourstorageaccount \
  --public-access off
```

### 6.3 Get Connection String
```bash
az storage account show-connection-string \
  --name yourstorageaccount \
  --resource-group rg-accommodation-form \
  --query connectionString --output tsv
```

## Email Configuration Guide

### Gmail SMTP Setup
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"
3. **Use App Password** as `EMAIL_SMTP_PASSWORD`

### Environment Variables for Gmail:
```
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-16-character-app-password
EMAIL_USE_SSL=true
```

## Troubleshooting

### Common Issues

1. **App Won't Start**
   - Check environment variables are set correctly
   - Verify startup.sh has execute permissions
   - Check application logs: `az webapp log tail`

2. **Email Not Working**
   - Verify SMTP credentials and server settings
   - Check firewall/security settings for email provider
   - Test with a simple email service first

3. **Static Files Not Loading**
   - Verify static files are included in deployment package
   - Check file paths in templates match static file structure

4. **Import Errors**
   - Ensure all dependencies are in requirements.txt
   - Check Python version compatibility (3.12)

### Viewing Logs
```bash
# Stream live logs
az webapp log tail \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app

# Download log files
az webapp log download \
  --resource-group rg-accommodation-form \
  --name accommodation-form-app
```

## Security Considerations

1. **Environment Variables**: Never commit secrets to source control
2. **HTTPS**: Always use HTTPS in production (enabled by default on azurewebsites.net)
3. **Firewall**: Configure App Service firewall rules as needed
4. **Secrets Management**: Consider using Azure Key Vault for secrets
5. **CORS**: Configure ALLOWED_ORIGINS restrictively
6. **Secret Key**: Use a long, random secret key for production

## Maintenance

### Updating the Application
1. Download new deployment_package.zip
2. Deploy using same ZIP deploy method:
   ```bash
   az webapp deploy \
     --resource-group rg-accommodation-form \
     --name accommodation-form-app \
     --src-path ./deployment_package.zip \
     --type zip
   ```
3. Verify environment variables are still configured
4. Test functionality after deployment

### Monitoring
- Use Application Insights for monitoring and logging
- Set up alerts for application errors
- Monitor resource usage in Azure Portal

### Scaling
```bash
# Scale up to higher SKU
az appservice plan update \
  --name asp-accommodation-form \
  --resource-group rg-accommodation-form \
  --sku S1

# Scale out to multiple instances
az webapp scale \
  --name accommodation-form-app \
  --resource-group rg-accommodation-form \
  --instance-count 2
```

## Support Resources

- **Azure App Service Documentation**: https://docs.microsoft.com/en-us/azure/app-service/
- **Python on Azure App Service**: https://docs.microsoft.com/en-us/azure/app-service/configure-language-python
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

---

**Note**: This deployment package is production-ready but requires manual environment variable configuration. All secrets and configuration files have been excluded for security purposes. Reference the `.env.example` file for all available configuration options.