# 🚀 Quick Start Guide

**Deploy Azure Accommodation Form in 15 minutes**

## What's in this package?

📁 **Essential Files:**
- `main.py` - Main application file
- `requirements.txt` - Python dependencies  
- `app/` - Application source code
- `startup.sh` - Azure startup script
- `web.config` - Azure configuration

📖 **Documentation:**
- `README_DEPLOYMENT.md` - Complete step-by-step guide
- `AZURE_CONFIG.txt` - Configuration template
- `QUICK_START.md` - This file

## ⚡ Fast Deploy (5 Steps)

### 1. Create Azure Storage
- Azure Portal → Create Resource → Storage Account
- Save the connection string

### 2. Create Azure Web App  
- Azure Portal → Create Resource → Web App
- Runtime: Python 3.12, OS: Linux

### 3. Upload this Package
- Web App → Deployment Center → ZIP Deploy
- Upload the entire folder as ZIP

### 4. Configure Settings
- Web App → Configuration → Application settings
- Use `AZURE_CONFIG.txt` as your template
- Edit `appsettings.json` with your settings

### 5. Test Your App
- Visit your app URL
- Test form submission

## 📧 Email Setup (Most Common)

**Gmail Users:**
1. Enable 2-factor authentication
2. Create App Password
3. Use these settings:
   - Server: `smtp.gmail.com`
   - Port: `587`
   - Username: Your Gmail
   - Password: App Password (not regular password)

## 🔧 Configuration via appsettings.json

**✅ No environment variables needed!** Just edit the `appsettings.json` file:

```json
{
  "ServerSettings": {
    "Environment": "production",
    "SecretKey": "[50+ character random password]"
  },
  "EmailSettings": {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "SmtpUsername": "[your email]",
    "SmtpPassword": "[app password]",
    "FromEmail": "[your email]",
    "CompanyEmail": "[where forms go]"
  },
  "BlobStorageSettings": {
    "ConnectionString": "[from storage account]"
  },
  "ApplicationSettings": {
    "ApplicationUrl": "https://[your-app].azurewebsites.net"
  }
}
```

## ⚠️ Common Issues

**App won't start?**
- Check all settings are configured in `appsettings.json`
- Verify storage connection string
- Restart the app

**No emails?**
- Use App Password for Gmail (not regular password)
- Check SMTP settings
- Test with simple email first

**Files won't upload?**
- Check storage connection string
- Verify container name: `form-submissions`

## 📞 Need Help?

1. **Read the full guide:** `README_DEPLOYMENT.md`
2. **Check Azure logs:** Web App → Log stream
3. **Verify settings:** Use `AZURE_CONFIG.txt` template

## 💡 Pro Tips

- Start with Basic tier for testing
- Use strong SECRET_KEY (password generator recommended)
- Test email settings before going live
- Monitor costs in Azure Portal
- Keep configuration backed up

---

**Ready?** Open `README_DEPLOYMENT.md` for the complete guide!