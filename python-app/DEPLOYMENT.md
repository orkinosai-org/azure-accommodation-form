# Deployment Guide - Azure Accommodation Form

This guide covers deploying the Python-based Azure Accommodation Form to Azure App Service.

## Prerequisites

- Azure subscription
- Azure CLI installed
- Git repository with the application code
- Domain name (optional, for custom domains)

## Quick Deployment

### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-accommodation-form --location "East US"

# Create App Service plan
az appservice plan create \
  --name plan-accommodation-form \
  --resource-group rg-accommodation-form \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group rg-accommodation-form \
  --plan plan-accommodation-form \
  --name your-app-name \
  --runtime "PYTHON|3.11"
```

### 2. Create Azure Blob Storage

```bash
# Create storage account
az storage account create \
  --name storageaccommodationform \
  --resource-group rg-accommodation-form \
  --location "East US" \
  --sku Standard_LRS

# Get connection string
az storage account show-connection-string \
  --name storageaccommodationform \
  --resource-group rg-accommodation-form
```

### 3. Configure App Settings

```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group rg-accommodation-form \
  --name your-app-name \
  --settings \
    ENVIRONMENT=production \
    SECRET_KEY="your-production-secret-key" \
    SMTP_SERVER="smtp.gmail.com" \
    SMTP_PORT=587 \
    SMTP_USERNAME="your-email@gmail.com" \
    SMTP_PASSWORD="your-app-password" \
    FROM_EMAIL="noreply@yourdomain.com" \
    ADMIN_EMAIL="admin@yourdomain.com" \
    AZURE_STORAGE_CONNECTION_STRING="your-connection-string" \
    CAPTCHA_SITE_KEY="your-captcha-site-key" \
    CAPTCHA_SECRET_KEY="your-captcha-secret-key" \
    ADMIN_TOKEN="your-secure-admin-token"
```

### 4. Deploy Code

```bash
# Deploy from Git
az webapp deployment source config \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --repo-url https://github.com/yourusername/yourrepo \
  --branch main \
  --manual-integration
```

## Detailed Configuration

### Email Configuration

#### Gmail SMTP
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Use the App Password as SMTP_PASSWORD

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
```

#### Azure Communication Services (Alternative)
```bash
# Create Communication Service
az communication create \
  --name comm-accommodation-form \
  --resource-group rg-accommodation-form \
  --location "Global"

# Get connection string
az communication show \
  --name comm-accommodation-form \
  --resource-group rg-accommodation-form
```

### SSL/TLS Configuration

#### Custom Domain with SSL
```bash
# Map custom domain
az webapp config hostname add \
  --webapp-name your-app-name \
  --resource-group rg-accommodation-form \
  --hostname yourdomain.com

# Enable SSL
az webapp config ssl bind \
  --certificate-thumbprint your-cert-thumbprint \
  --ssl-type SNI \
  --name your-app-name \
  --resource-group rg-accommodation-form
```

#### Client Certificate Authentication
```bash
# Require client certificates
az webapp update \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --client-cert-enabled true
```

### CAPTCHA Setup

#### reCAPTCHA (Google)
1. Go to [Google reCAPTCHA](https://www.google.com/recaptcha/)
2. Create a new site (reCAPTCHA v2)
3. Add your domain
4. Get site key and secret key

#### hCaptcha (Alternative)
1. Go to [hCaptcha](https://www.hcaptcha.com/)
2. Create account and site
3. Get site key and secret key

### Monitoring and Logging

#### Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app insights-accommodation-form \
  --location "East US" \
  --resource-group rg-accommodation-form

# Get instrumentation key
az monitor app-insights component show \
  --app insights-accommodation-form \
  --resource-group rg-accommodation-form
```

#### Configure logging
```bash
az webapp log config \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --application-logging filesystem \
  --level information
```

## GitHub Actions Setup

### 1. Get Publish Profile
```bash
az webapp deployment list-publishing-profiles \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --xml
```

### 2. Add GitHub Secrets
In your GitHub repository settings, add these secrets:
- `AZURE_WEBAPP_PUBLISH_PROFILE` - The XML content from step 1
- Other sensitive configuration values

### 3. Configure Workflow
The workflow file is already provided in `.github/workflows/deploy.yml`

## Security Considerations

### Network Security
```bash
# Restrict access to specific IPs (optional)
az webapp config access-restriction add \
  --resource-group rg-accommodation-form \
  --name your-app-name \
  --rule-name "Office IP" \
  --action Allow \
  --ip-address 203.0.113.0/24 \
  --priority 100
```

### Application Security
- Use strong, unique SECRET_KEY
- Configure HTTPS-only access
- Enable client certificate authentication
- Use secure SMTP passwords
- Regularly rotate API keys

### Data Protection
- Enable Azure Blob Storage encryption
- Configure access policies
- Enable audit logging
- Regular security updates

## Testing Deployment

### Health Check
```bash
curl https://your-app-name.azurewebsites.net/health
```

### Certificate Test
```bash
curl -X POST https://your-app-name.azurewebsites.net/api/auth/verify-certificate
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test concurrent users
ab -n 100 -c 10 https://your-app-name.azurewebsites.net/
```

## Maintenance

### Scaling
```bash
# Scale up
az appservice plan update \
  --name plan-accommodation-form \
  --resource-group rg-accommodation-form \
  --sku P1V2

# Scale out
az webapp scale \
  --name your-app-name \
  --resource-group rg-accommodation-form \
  --instance-count 3
```

### Backup
```bash
# Configure automated backups
az webapp config backup create \
  --resource-group rg-accommodation-form \
  --webapp-name your-app-name \
  --backup-name daily-backup \
  --storage-account-url "https://storageaccommodationform.blob.core.windows.net/backups" \
  --frequency-interval 1 \
  --frequency-unit Day \
  --retain-one true
```

### Updates
```bash
# Update app settings
az webapp config appsettings set \
  --resource-group rg-accommodation-form \
  --name your-app-name \
  --settings NEW_SETTING="new-value"

# Restart app
az webapp restart \
  --name your-app-name \
  --resource-group rg-accommodation-form
```

## Troubleshooting

### View Logs
```bash
# Stream logs
az webapp log tail \
  --name your-app-name \
  --resource-group rg-accommodation-form

# Download logs
az webapp log download \
  --name your-app-name \
  --resource-group rg-accommodation-form
```

### Common Issues

1. **SMTP Authentication Failed**
   - Check Gmail App Password
   - Verify SMTP settings
   - Test with telnet

2. **Blob Storage Access Denied**
   - Verify connection string
   - Check container permissions
   - Ensure container exists

3. **CAPTCHA Verification Failed**
   - Check site key/secret key
   - Verify domain configuration
   - Test in browser

4. **Certificate Authentication Issues**
   - Verify client certificate
   - Check certificate chain
   - Review SSL configuration

### Getting Help
- Check Azure Portal diagnostics
- Review Application Insights
- Monitor resource usage
- Contact Azure support if needed