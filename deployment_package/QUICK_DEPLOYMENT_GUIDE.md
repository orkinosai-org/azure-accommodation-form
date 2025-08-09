# Quick Start: Deploy to Your New Azure Web App

This guide shows you how to quickly configure deployment to your newly created Azure Web App.

## Step-by-Step Example

### 1. Create Your Azure Web App
In Azure Portal, create a new Web App:
- **App Name**: `my-accommodation-app-test` (note this name)
- **Runtime**: Python 3.12
- **Operating System**: Linux

### 2. Get Your Publish Profile
1. Go to your Web App in Azure Portal
2. Click **Get publish profile** button
3. Download the `.PublishSettings` file
4. Copy the entire contents of this file

### 3. Configure GitHub Secret
1. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
4. Value: Paste the entire contents of the `.PublishSettings` file
5. Click **Add secret**

### 4. Update Configuration
Edit `python-app/appsettings.json` and update the `DeploymentSettings` section:

```json
{
  "DeploymentSettings": {
    "AzureWebAppName": "my-accommodation-app-test",
    "PythonVersion": "3.12",
    "AzurePublishProfileSecret": "AZURE_WEBAPP_PUBLISH_PROFILE",
    "Environment": "production"
  }
}
```

### 5. Validate Configuration (Optional)
Test your configuration locally:

```bash
cd python-app
python validate_deployment_config.py
```

You should see:
```
🎉 All validation tests passed!

📋 Ready for deployment with these settings:
   • Azure Web App: my-accommodation-app-test
   • Python Version: 3.12
   • Environment: production
   • GitHub Secret: AZURE_WEBAPP_PUBLISH_PROFILE
```

### 6. Deploy
1. Commit your changes:
   ```bash
   git add python-app/appsettings.json
   git commit -m "Configure deployment for my-accommodation-app-test"
   ```

2. Push to main branch:
   ```bash
   git push origin main
   ```

### 7. Monitor Deployment
1. Go to **Actions** tab in your GitHub repository
2. Watch the **Deploy Python App to Azure** workflow
3. The workflow will show your configuration:
   ```
   📋 Configuration loaded from appsettings.json:
     Azure Web App Name: my-accommodation-app-test
     Python Version: 3.12
     Publish Profile Secret: AZURE_WEBAPP_PUBLISH_PROFILE
   ```

### 8. Verify Deployment
Once deployment completes, visit:
`https://my-accommodation-app-test.azurewebsites.net/health`

You should see:
```json
{
  "status": "healthy",
  "service": "Azure Accommodation Form",
  "version": "1.0.0",
  "environment": "production"
}
```

## Testing Multiple Environments

### Scenario: Add a Staging Environment

1. **Create staging Web App**: `my-accommodation-app-staging`
2. **Add staging secret**: `AZURE_STAGING_PUBLISH_PROFILE`
3. **Create staging branch** and update configuration:
   ```json
   {
     "DeploymentSettings": {
       "AzureWebAppName": "my-accommodation-app-staging",
       "PythonVersion": "3.12",
       "AzurePublishProfileSecret": "AZURE_STAGING_PUBLISH_PROFILE",
       "Environment": "staging"
     }
   }
   ```

### Scenario: Update Existing Production App

To deploy to a different production app:

1. Update `AzureWebAppName` in your configuration
2. Add the new publish profile as a GitHub secret
3. Push to main branch

The workflow automatically adapts to your configuration!

## Troubleshooting

**❌ "Web App not found"**
- Double-check the `AzureWebAppName` matches exactly
- Verify the Web App exists and is running in Azure

**❌ "Authentication failed"**  
- Ensure the publish profile secret is correctly configured
- Check that the secret name matches `AzurePublishProfileSecret`

**❌ "Configuration error"**
- Run `python validate_deployment_config.py` to check your configuration
- Verify JSON syntax is correct

## Success! 🎉

Your Azure Web App is now configured for automatic deployment. Every push to the main branch will:

1. ✅ Build with Python 3.12
2. ✅ Run tests and security scans  
3. ✅ Deploy to your specified Azure Web App
4. ✅ Use your environment-specific secrets

**Next time you need to deploy to a different Azure Web App, just update the `DeploymentSettings` in `appsettings.json`!**