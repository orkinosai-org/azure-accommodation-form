# Azure Accommodation Form - Client Deployment Guide

**Welcome!** This guide will help you deploy your Azure Accommodation Form application. Don't worry if you're not technical - we've made this as simple as possible.

## 📦 What's in this package?

This deployment package contains everything you need:
- ✅ **Ready-to-deploy application files**
- ✅ **Configuration template with clear instructions**
- ✅ **Step-by-step deployment guide**

## 🚀 Quick Start (2 Options)

### Option A: Edit Configuration Before Deployment (Recommended)
1. Open `appsettings.json` in any text editor
2. Replace placeholder values with your real information
3. Deploy to Azure
4. Done!

### Option B: Deploy First, Configure Later
1. Deploy the package to Azure as-is
2. Configure settings through Azure Portal
3. Restart your application

## 📝 Step 1: Configure Your Settings

### Open the Configuration File
1. Find the file named `appsettings.json` in your deployment package
2. Open it with any text editor (Notepad, Visual Studio Code, etc.)
3. You'll see placeholder values that need to be replaced

### Required Settings to Replace

#### 🗄️ Database Connection
```json
"DefaultConnection": "Server=YOUR_SQL_SERVER_NAME.database.windows.net;Database=YOUR_DATABASE_NAME;User Id=YOUR_DATABASE_USERNAME;Password=YOUR_DATABASE_PASSWORD;Encrypt=True;TrustServerCertificate=False;"
```
**Replace with your Azure SQL Database details**

#### 📧 Email Settings (for notifications)
```json
"SmtpUsername": "YOUR_EMAIL@gmail.com",
"SmtpPassword": "YOUR_APP_PASSWORD",
"CompanyEmail": "admin@yourdomain.com"
```

**For Gmail users:**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Security → 2-Step Verification → App Passwords
3. Generate an app password and use it (not your regular password)

#### 💾 File Storage Settings
```json
"ConnectionString": "DefaultEndpointsProtocol=https;AccountName=YOUR_STORAGE_ACCOUNT_NAME;AccountKey=YOUR_STORAGE_ACCOUNT_KEY;EndpointSuffix=core.windows.net"
```
**Get this from Azure Portal → Storage Accounts → Access Keys**

#### 🌐 Application URL
```json
"ApplicationUrl": "https://YOUR_APP_NAME.azurewebsites.net"
```
**Replace with your Azure Web App URL**

## 🔧 Step 2: Deploy to Azure

### Prerequisites
- Azure subscription
- Azure Web App created (with .NET 8 runtime)
- Azure Storage Account created
- Azure SQL Database created (optional, can use SQLite for testing)

### Deployment Methods

#### Method A: Azure Portal (Easiest)
1. Go to Azure Portal → Your Web App
2. Click "Deployment Center"
3. Choose "Local Git" or "ZIP Deploy"
4. Upload your configured files
5. Wait for deployment to complete

#### Method B: Azure CLI
```bash
# Create a ZIP file of your configured package
zip -r myapp.zip . -x "*.git*" "*.DS_Store*"

# Deploy to Azure
az webapp deployment source config-zip \
  --name YOUR_APP_NAME \
  --resource-group YOUR_RESOURCE_GROUP \
  --src myapp.zip
```

## ⚙️ Step 3: Configure Settings via Azure Portal (Alternative)

If you chose Option B or want to change settings later:

1. Go to Azure Portal → Your Web App
2. Click "Configuration" → "Application Settings"
3. Add these settings:

| Setting Name | Example Value |
|--------------|---------------|
| `ConnectionStrings__DefaultConnection` | Your database connection string |
| `EmailSettings__SmtpUsername` | your-email@gmail.com |
| `EmailSettings__SmtpPassword` | your-app-password |
| `EmailSettings__CompanyEmail` | admin@yourdomain.com |
| `BlobStorageSettings__ConnectionString` | Your storage connection string |
| `ApplicationSettings__ApplicationUrl` | https://yourapp.azurewebsites.net |

4. Click "Save"
5. Restart your application

## 🧪 Step 4: Test Your Application

1. **Visit your application URL**
   - Go to `https://YOUR_APP_NAME.azurewebsites.net`
   - You should see the accommodation form

2. **Test form submission**
   - Fill out a test form
   - Submit it
   - Check if you receive an email notification

3. **Check file storage**
   - Verify files are saved in your Azure Storage Account
   - Go to Azure Portal → Storage Account → Containers → form-submissions

## ❗ Troubleshooting

### Application won't start
- **Check logs**: Azure Portal → Your Web App → Log Stream
- **Verify runtime**: Make sure .NET 8 is selected
- **Check configuration**: Ensure all required settings are provided

### Emails not sending
- **Verify Gmail settings**: Use App Password, not regular password
- **Check SMTP settings**: Server should be `smtp.gmail.com`, Port `587`
- **Test email account**: Try sending email manually with the same settings

### File uploads failing
- **Check storage connection**: Verify connection string is correct
- **Container exists**: Make sure "form-submissions" container exists
- **Permissions**: Ensure storage account allows access

### Database errors
- **Connection string**: Verify server name, database name, username, password
- **Firewall**: Ensure Azure services can access your SQL database
- **Alternative**: Use SQLite for testing: `"Data Source=FormSubmissions.db"`

## 🔐 Security Notes

- **Never share your configuration files** with real passwords
- **Use Azure Key Vault** for production secrets (advanced)
- **Enable HTTPS only** in Azure Web App settings
- **Regular backups** of your database and storage

## 📞 Need Help?

### Self-Help Resources
1. **Check the error logs** in Azure Portal first
2. **Review configuration** - most issues are configuration-related
3. **Test each component** individually (email, storage, database)

### Common Configuration Issues
- Using regular password instead of App Password for Gmail
- Incorrect storage account connection string format
- Wrong database server name or credentials
- Application URL doesn't match actual Azure Web App URL

### Getting Support
- **Azure Support**: For Azure-specific issues
- **Email Provider**: For SMTP configuration help
- **Database Issues**: Verify connection strings and firewall settings

---

## 📋 Configuration Checklist

Before deploying, ensure you have:

- [ ] ✅ Azure Web App created with .NET 8 runtime
- [ ] ✅ Azure Storage Account with "form-submissions" container
- [ ] ✅ Email account with SMTP access (Gmail App Password)
- [ ] ✅ Database connection (Azure SQL or SQLite for testing)
- [ ] ✅ Replaced all placeholder values in appsettings.json
- [ ] ✅ Application URL updated to match your Azure Web App
- [ ] ✅ Tested email configuration separately if possible

**Once everything is checked, you're ready to deploy! 🚀**

---

*This deployment package was created to make your life easier. If you have suggestions for improvement, please let us know!*