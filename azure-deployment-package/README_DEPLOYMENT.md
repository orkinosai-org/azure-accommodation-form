# Azure Accommodation Form - Easy Deployment Guide

**For Non-Technical Users - Deploy to Azure App Service Using Azure Portal Only**

This guide will help you deploy the Azure Accommodation Form application to Microsoft Azure without needing any technical knowledge, command line tools, or programming experience. You'll only use your web browser and the Azure Portal.

## 📋 What You'll Need

Before starting, make sure you have:

✅ **Microsoft Azure account** (create one at [azure.microsoft.com](https://azure.microsoft.com))  
✅ **Azure subscription** (free tier works fine)  
✅ **Email account for SMTP** (Gmail, Outlook, or business email)  
✅ **Web browser** (Chrome, Firefox, Edge, or Safari)  
✅ **This deployment package** (the ZIP file you downloaded)

## 🚀 Step-by-Step Deployment

### Step 1: Create Azure Storage Account

Your application needs a place to store submitted forms securely.

1. **Open Azure Portal**
   - Go to [portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure account

2. **Create Storage Account**
   - Click **"Create a resource"** (+ icon in top left)
   - Search for **"Storage account"**
   - Click **"Storage account"** then **"Create"**

3. **Configure Storage Account**
   - **Subscription**: Select your subscription
   - **Resource group**: Click **"Create new"** and name it `accommodation-form-rg`
   - **Storage account name**: Choose a unique name (letters and numbers only, no spaces)
     - Example: `accommodationforms2024`
   - **Region**: Choose closest to your users (e.g., East US, West Europe)
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS)
   - Click **"Review + create"** then **"Create"**

4. **Get Storage Connection String**
   - Wait for deployment to complete (2-3 minutes)
   - Click **"Go to resource"**
   - In left menu, click **"Access keys"**
   - Copy the entire **"Connection string"** from key1
   - **Save this in a text file** - you'll need it later

### Step 2: Create Azure Web App

This is where your application will run.

1. **Create Web App**
   - In Azure Portal, click **"Create a resource"**
   - Search for **"Web App"**
   - Click **"Web App"** then **"Create"**

2. **Configure Web App**
   - **Subscription**: Select your subscription
   - **Resource Group**: Use existing `accommodation-form-rg`
   - **Name**: Choose unique name for your app
     - Example: `my-accommodation-form-app`
     - This will be your website URL: `https://my-accommodation-form-app.azurewebsites.net`
   - **Publish**: Code
   - **Runtime stack**: Python 3.12
   - **Operating System**: Linux
   - **Region**: Same as storage account
   - **App Service Plan**: Create new
     - **Name**: `accommodation-form-plan`
     - **Pricing tier**: Click **"Explore pricing options"**
       - For testing: Choose **Basic B1** ($13/month)
       - For production: Choose **Standard S1** ($56/month)

3. **Create the App**
   - Click **"Review + create"**
   - Click **"Create"**
   - Wait for deployment (3-5 minutes)
   - Click **"Go to resource"**

### Step 3: Configure Application Settings

Before uploading your app, you need to edit the configuration file with your settings.

1. **Edit appsettings.json in the Deployment Package**
   - Open the `appsettings.json` file in this deployment package
   - Replace ALL placeholder values with your real information (see examples below)

2. **Required Settings to Update:**

   **Email Settings (Required for form submissions):**
   ```json
   "EmailSettings": {
     "SmtpServer": "smtp.gmail.com",
     "SmtpPort": 587,
     "SmtpUsername": "YOUR_EMAIL@gmail.com",          ← Your Gmail address
     "SmtpPassword": "YOUR_GMAIL_APP_PASSWORD",       ← See Gmail setup below
     "UseSsl": true,
     "FromEmail": "noreply@yourdomain.com",           ← Email forms will come from
     "FromName": "Azure Accommodation Form",
     "CompanyEmail": "admin@yourdomain.com"           ← Where forms will be sent to
   }
   ```

   **Storage Settings:**
   ```json
   "BlobStorageSettings": {
     "ConnectionString": "[Paste your storage connection string here]",
     "ContainerName": "form-submissions"
   }
   ```

   **Application Settings:**
   ```json
   "ApplicationSettings": {
     "ApplicationName": "Azure Accommodation Form",
     "ApplicationUrl": "https://YOUR_APP_NAME.azurewebsites.net/",
     "TokenExpirationMinutes": 15,
     "TokenLength": 6
   }
   ```

   **Security Settings:**
   ```json
   "ServerSettings": {
     "Environment": "production",
     "SecretKey": "CHANGE_THIS_TO_A_LONG_RANDOM_STRING_IN_PRODUCTION",
     "AllowedHosts": ["YOUR_APP_NAME.azurewebsites.net"],
     "AllowedOrigins": ["https://YOUR_APP_NAME.azurewebsites.net"]
   }
   ```

3. **Save the File**
   - Save the `appsettings.json` file with your changes
   - The app will read all settings from this file when deployed

### Step 4: Deploy Your Application

Now upload the application code.

1. **Open Deployment Center**
   - In your Web App, click **"Deployment Center"** in left menu

2. **Upload ZIP File**
   - Click **"Local Git"** tab
   - Click **"ZIP Deploy"**
   - Click **"Browse"** and select your `azure-deployment-package.zip` file
   - Click **"Upload"**
   - Wait for deployment (5-10 minutes)

3. **Verify Deployment**
   - Go to **"Overview"** in left menu
   - Click your app's URL (e.g., `https://my-accommodation-form-app.azurewebsites.net`)
   - You should see the application home page

### Step 5: Test Your Application

1. **Basic Test**
   - Visit your app URL
   - You should see the accommodation form
   - Try filling out the form with test data

2. **Email Test**
   - Complete a test form submission
   - Check that you receive the email confirmation
   - Check that the company receives the form

## 📧 Email Configuration Guide

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to [myaccount.google.com](https://myaccount.google.com)
   - Click **"Security"**
   - Enable **"2-Step Verification"**

2. **Create App Password**
   - In Security settings, click **"App passwords"**
   - Select **"Mail"** and **"Other"**
   - Name it **"Azure Accommodation Form"**
   - Copy the 16-character password
   - Use this as your `EMAIL_SMTP_PASSWORD`

### Outlook/Hotmail Setup

Use these settings:
- **SMTP Server**: `smtp-mail.outlook.com`
- **Port**: `587`
- **Username**: Your full Outlook email
- **Password**: Your account password or app password

### Business Email Setup

Contact your IT department for:
- SMTP server address
- Port number (usually 587 or 465)
- Authentication requirements

## 🔧 Configuration Reference

This app uses a single `appsettings.json` file for all configuration. Below are the settings you need to update:

### Required Settings
| Configuration Section | Setting | Description | Example |
|----------------------|---------|-------------|---------|
| `ServerSettings` | `Environment` | Application mode | `production` |
| `ServerSettings` | `SecretKey` | Security key (50+ random characters) | `your-very-long-random-secret-key-here` |
| `EmailSettings` | `SmtpServer` | Email server | `smtp.gmail.com` |
| `EmailSettings` | `SmtpPort` | Email port | `587` |
| `EmailSettings` | `SmtpUsername` | Your email | `youremail@gmail.com` |
| `EmailSettings` | `SmtpPassword` | Email password/app password | `your-app-password` |
| `EmailSettings` | `FromEmail` | From address | `youremail@gmail.com` |
| `EmailSettings` | `FromName` | From name | `Azure Accommodation Form` |
| `EmailSettings` | `CompanyEmail` | Where forms are sent | `admin@yourcompany.com` |
| `BlobStorageSettings` | `ConnectionString` | Azure Storage connection | `DefaultEndpointsProtocol=https;AccountName=...` |
| `BlobStorageSettings` | `ContainerName` | Storage container | `form-submissions` |
| `ApplicationSettings` | `ApplicationName` | App title | `Azure Accommodation Form` |
| `ApplicationSettings` | `ApplicationUrl` | Your app URL | `https://yourapp.azurewebsites.net` |

### Optional Settings
| Configuration Section | Setting | Description | Default |
|----------------------|---------|-------------|---------|
| `ApplicationSettings` | `TokenExpirationMinutes` | Email verification timeout | `15` |
| `ApplicationSettings` | `TokenLength` | Verification code length | `6` |

### Important Notes:
- ✅ **All settings are configured in the `appsettings.json` file**
- ✅ **No environment variables needed in Azure Portal**
- ✅ **Simple file editing - no technical knowledge required**
- ✅ **Update settings by editing the file before deployment**

## 🚨 Troubleshooting

### Common Issues and Solutions

#### "Application Error" or 500 Error
**Problem**: App won't start or shows error page

**Solutions**:
1. **Check Configuration File**
   - Open `appsettings.json` in the deployment package
   - Verify all required settings have real values (not placeholders)
   - Check for typos in setting names and values

2. **Check Storage Connection**
   - Test the storage connection string in BlobStorageSettings
   - Ensure storage account is accessible

3. **Check Email Settings**
   - Verify SMTP settings in EmailSettings section
   - Test with a simple email first

#### "Email Sending Failed"
**Problem**: Form submits but no emails are sent

**Solutions**:
1. **Gmail Issues**
   - Ensure 2-factor authentication is enabled
   - Use App Password, not account password
   - Check Gmail security settings

2. **SMTP Settings**
   - Verify server name and port
   - Check username is full email address
   - Ensure "Less secure app access" is enabled (if not using app password)

#### "File Upload Error"
**Problem**: Forms fail when uploading files

**Solutions**:
1. **Storage Issues**
   - Check storage connection string
   - Verify container name matches setting
   - Ensure storage account is in same region

2. **File Size Issues**
   - Files must be under 10MB
   - Only PDF, JPG, JPEG, PNG files allowed

#### "Page Not Found" or 404 Error
**Problem**: App URL shows "page not found"

**Solutions**:
1. **Deployment Issues**
   - Re-upload the ZIP file
   - Check deployment logs in Deployment Center
   - Restart the app in Overview page

2. **Configuration Issues**
   - Verify Python 3.12 runtime is selected
   - Check app service plan is running

### Certificate/SSL Issues
**Problem**: Certificate verification errors

**Solutions**:
1. **Force HTTPS**
   - In Configuration → General settings
   - Set "HTTPS Only" to On

2. **Certificate Problems**
   - Azure automatically provides SSL certificates
   - No additional configuration needed for .azurewebsites.net domains

### Missing Dependencies
**Problem**: "Module not found" errors

**Solutions**:
1. **Requirements File**
   - Ensure requirements.txt is in the ZIP file
   - Check all dependencies are listed

2. **Python Version**
   - Verify Python 3.12 is selected in Configuration

## 📊 Finding Application Logs

When something goes wrong, logs help identify the problem.

### Access Logs in Azure Portal

1. **Log Stream (Real-time)**
   - Go to your Web App
   - Click **"Log stream"** in left menu
   - Watch live logs as users access your app

2. **Application Insights (Detailed)**
   - Go to your Web App
   - Click **"Application Insights"** in left menu
   - Click **"View Application Insights data"**
   - Browse logs, errors, and performance data

3. **Kudu Console (Advanced)**
   - Go to **"Advanced Tools"** in left menu
   - Click **"Go"** to open Kudu
   - Navigate to LogFiles → Application

### Understanding Log Messages

**Normal Messages** (These are good):
```
INFO: Application startup complete
INFO: Uvicorn running on 0.0.0.0:8000
INFO: Configuration audit complete
```

**Warning Messages** (Check but not critical):
```
WARNING: Email configuration using legacy format
WARNING: Missing optional configuration
```

**Error Messages** (Need attention):
```
ERROR: Failed to connect to storage account
ERROR: SMTP authentication failed
ERROR: Configuration validation failed
```

## 🔐 Security Best Practices

### Protecting Your Application

1. **Strong Passwords**
   - Use complex SECRET_KEY (50+ characters)
   - Use App Passwords for email, not account passwords
   - Change default admin tokens

2. **Access Control**
   - Enable HTTPS-only access
   - Consider IP restrictions for admin access
   - Regularly review application settings

3. **Data Protection**
   - Form data is encrypted in storage
   - No sensitive data stored in databases
   - PDF files are secure in Azure Blob Storage

### Regular Maintenance

1. **Monthly Tasks**
   - Check application logs for errors
   - Verify email delivery is working
   - Review storage usage

2. **Security Updates**
   - Monitor Azure security advisories
   - Keep application dependencies updated
   - Review access logs periodically

## 💰 Cost Management

### Expected Costs (Monthly)

**Basic Setup**:
- Web App (Basic B1): ~$13/month
- Storage Account: ~$1-5/month (depending on usage)
- **Total**: ~$14-18/month

**Production Setup**:
- Web App (Standard S1): ~$56/month
- Storage Account: ~$5-15/month
- Application Insights: ~$2-10/month
- **Total**: ~$63-81/month

### Cost Optimization Tips

1. **Start Small**
   - Begin with Basic tier
   - Upgrade when needed

2. **Monitor Usage**
   - Check storage usage monthly
   - Scale down during low usage periods

3. **Clean Up**
   - Delete test resources when done
   - Archive old form submissions

## 📞 Support and Help

### Getting Help

1. **Azure Support**
   - Basic support included with subscription
   - Create support tickets in Azure Portal

2. **Application Issues**
   - Check this troubleshooting guide first
   - Review application logs
   - Contact your technical team if available

3. **Email Provider Support**
   - Gmail: [support.google.com](https://support.google.com)
   - Outlook: [support.microsoft.com](https://support.microsoft.com)

### Common Support Scenarios

**"My form stopped working"**
1. Check application logs
2. Verify email settings haven't changed
3. Test storage account access

**"I need to change email settings"**
1. Go to Configuration → Application settings
2. Update email-related variables
3. Save and restart application

**"I want to add more features"**
- This requires development work
- Contact a developer or technical team
- Consider hiring Azure consultants

---

## ✅ Quick Checklist

Before going live:

- [ ] Azure Storage Account created and connection string saved
- [ ] Azure Web App created with Python 3.12
- [ ] All required settings configured in appsettings.json
- [ ] Application deployed successfully
- [ ] Email settings tested and working
- [ ] Form submission tested end-to-end
- [ ] Application accessible at public URL
- [ ] HTTPS enabled and working
- [ ] Application logs reviewed for errors

## 🎉 Congratulations!

You've successfully deployed the Azure Accommodation Form! Your application is now running in the cloud and ready to accept form submissions.

**Your app is available at**: `https://[your-app-name].azurewebsites.net`

Remember to:
- Test the form thoroughly before sharing with users
- Monitor the application logs regularly
- Keep your email credentials secure
- Back up important configuration settings

---

*This guide was created for non-technical users. If you encounter issues beyond this guide, consider consulting with a technical professional or Azure expert.*