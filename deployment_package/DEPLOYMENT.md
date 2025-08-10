# Azure Accommodation Form - Deployment Guide for End Users

This guide provides **simple, step-by-step instructions** for deploying the Azure Accommodation Form application to Azure App Service. No technical expertise required!

## What You'll Need

Before starting, make sure you have:

1. **Azure account** with active subscription
2. **Email account** for sending form notifications (Gmail recommended)
3. **10-15 minutes** of your time

## Step 1: Configure Your Settings (IMPORTANT!)

### 🔧 Edit the Configuration File

1. **Open** the `appsettings.json` file in this deployment package
2. **Replace** the placeholder values with your real information:

#### Email Settings (Required for form submissions)
```json
"EmailSettings": {
  "SmtpUsername": "YOUR_EMAIL@gmail.com",          ← Your Gmail address
  "SmtpPassword": "YOUR_GMAIL_APP_PASSWORD",       ← See Gmail setup below
  "FromEmail": "noreply@yourdomain.com",           ← Email forms will come from
  "CompanyEmail": "admin@yourdomain.com"           ← Where forms will be sent to
}
```

#### Azure Storage (Required for file uploads)
```json
"BlobStorageSettings": {
  "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=YOURSTORAGEACCOUNT;AccountKey=YOUR_STORAGE_ACCOUNT_KEY;EndpointSuffix=core.windows.net"
}
```

#### Application Settings
```json
"ApplicationSettings": {
  "ApplicationUrl": "https://YOUR_APP_NAME.azurewebsites.net/"
}
```

#### Security Settings
```json
"ServerSettings": {
  "SecretKey": "CHANGE_THIS_TO_A_LONG_RANDOM_STRING_IN_PRODUCTION",
  "AllowedHosts": ["YOUR_APP_NAME.azurewebsites.net"],
  "AllowedOrigins": ["https://YOUR_APP_NAME.azurewebsites.net"]
}
```

### 📧 Gmail Setup (For Form Notifications)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com)
   - Click **Security** → **2-Step Verification** → **App Passwords**
   - Select **Mail** and generate a password
   - **Copy this password** and use it in `SmtpPassword` (NOT your regular Gmail password)

## Step 2: Deploy to Azure App Service

### Option A: Azure Portal (Easiest)

1. **Log into** [Azure Portal](https://portal.azure.com)
2. **Create App Service**:
   - Click "**Create a resource**"
   - Search for "**Web App**"
   - Click "**Create**"

3. **Configure Basic Settings**:
   - **Resource Group**: Create new or select existing
   - **Name**: Choose unique name (this becomes your URL: `https://YOUR_NAME.azurewebsites.net`)
   - **Runtime Stack**: **Python 3.12**
   - **Operating System**: **Linux**
   - **Region**: Choose closest to your users

4. **Create Azure Storage** (for file uploads):
   - Go to "**Create a resource**" → "**Storage Account**"
   - Use same **Resource Group** as your app
   - **Name**: Choose unique name (letters/numbers only)
   - **Performance**: Standard
   - **Replication**: LRS (cheapest)
   - After creation, go to "**Access Keys**" and copy the **Connection String**

5. **Deploy Your Files**:
   - Go to your **App Service** in Azure Portal
   - Click "**Deployment Center**"
   - Choose "**ZIP Deploy**"
   - **Upload** this entire deployment package as a ZIP file
   - Click "**Deploy**"

### Option B: Using Azure CLI (Advanced Users)

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-accommodation-form --location "East US"

# Create storage account
az storage account create --name yourstorageaccount --resource-group rg-accommodation-form --location "East US" --sku Standard_LRS

# Create App Service Plan
az appservice plan create --name asp-accommodation-form --resource-group rg-accommodation-form --sku B1 --is-linux

# Create Web App
az webapp create --name YOUR_APP_NAME --resource-group rg-accommodation-form --plan asp-accommodation-form --runtime "PYTHON:3.12"

# Deploy ZIP file
az webapp deployment source config-zip --name YOUR_APP_NAME --resource-group rg-accommodation-form --src deployment_package.zip
```

## Step 3: Configure Application Settings in Azure

### Method 1: Azure Portal (Recommended)

1. **Go to your App Service** in Azure Portal
2. **Click "Configuration"** in the left menu
3. **Add these Application Settings** (click "New application setting" for each):

| Name | Value |
|------|-------|
| `WEBSITES_PORT` | `8000` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

4. **Click "Save"** at the top

### Method 2: Update Configuration File After Deployment

1. **Go to your App Service** → **Development Tools** → **SSH**
2. **Navigate to**: `/home/site/wwwroot/`
3. **Edit** `appsettings.json` with your real values
4. **Restart** the app from Azure Portal

## Step 4: Test Your Application

1. **Visit your app URL**: `https://YOUR_APP_NAME.azurewebsites.net`
2. **Fill out a test form** to verify everything works
3. **Check your email** for form submissions (check spam folder too!)
4. **Verify files** are saved in Azure Storage

### Troubleshooting

#### App Won't Start
- **Check Logs**: Go to Azure Portal → Your App → **Monitoring** → **Log stream**
- **Common Issue**: Missing configuration values in `appsettings.json`

#### Email Not Working
- **Verify Gmail App Password** (not regular password!)
- **Check spam folder**
- **Test with a different email provider** if needed

#### Files Not Uploading
- **Verify Storage Account** connection string is correct
- **Check container exists**: Go to Storage Account → **Containers** → ensure "form-submissions" exists

## Step 5: Update Settings Later

### To Update Configuration After Deployment:

1. **Azure Portal Method**:
   - Go to **App Service** → **Development Tools** → **App Service Editor**
   - Edit `appsettings.json`
   - **Restart** the app

2. **Direct File Edit**:
   - Use **SSH** or **App Service Editor** to modify files
   - Always **restart** after changes

### To Update Application Files:

1. **Create new deployment ZIP** with your changes
2. **Go to Deployment Center** → **ZIP Deploy**
3. **Upload and deploy** new version

## Important Security Notes

🔒 **Never share your:**
- Gmail App Password
- Azure Storage Account Keys
- Secret Keys

🔒 **Always use HTTPS** (enabled by default on Azure App Service)

🔒 **Regularly update** your credentials and review access logs

## Support

### Common URLs After Deployment:
- **Your Application**: `https://YOUR_APP_NAME.azurewebsites.net`
- **Health Check**: `https://YOUR_APP_NAME.azurewebsites.net/health`
- **Configuration Status**: `https://YOUR_APP_NAME.azurewebsites.net/config-status`

### Getting Help:
1. **Check Azure Portal logs** first (Monitoring → Log stream)
2. **Test configuration** using the health check URL
3. **Review this guide** for missed steps
4. **Contact Azure Support** for Azure-specific issues

---

## Quick Checklist

Before deployment:
- [ ] Edited `appsettings.json` with your real values
- [ ] Set up Gmail App Password
- [ ] Created Azure Storage Account
- [ ] Chosen unique App Service name

After deployment:
- [ ] App starts without errors (check logs)
- [ ] Test form submission works
- [ ] Email notifications arrive
- [ ] Files upload to storage
- [ ] Configured HTTPS-only access

**Your accommodation form application is now ready to use!** 🎉