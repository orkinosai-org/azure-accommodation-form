# Azure Web App Deployment Configuration Guide

This guide explains how to configure automatic deployments to your Azure Web App using GitHub Actions and the `appsettings.json` configuration file.

## Overview

The deployment process is now configured through the `DeploymentSettings` section in `python-app/appsettings.json`. This allows you to easily switch between different Azure Web Apps for testing and production deployments by simply updating the configuration file.

## Configuration

### DeploymentSettings Section

Add or update the `DeploymentSettings` section in your `python-app/appsettings.json` file:

```json
{
  "DeploymentSettings": {
    "AzureWebAppName": "your-azure-webapp-name",
    "PythonVersion": "3.12",
    "AzurePublishProfileSecret": "AZURE_WEBAPP_PUBLISH_PROFILE",
    "Environment": "production"
  }
}
```

### Configuration Fields

| Field | Description | Default Value | Required |
|-------|-------------|---------------|----------|
| `AzureWebAppName` | The name of your Azure Web App (without .azurewebsites.net) | `azure-accommodation-form` | ✅ Yes |
| `PythonVersion` | Python runtime version to use | `3.12` | ✅ Yes |
| `AzurePublishProfileSecret` | Name of the GitHub secret containing publish profile | `AZURE_WEBAPP_PUBLISH_PROFILE` | ✅ Yes |
| `Environment` | Deployment environment name | `production` | ✅ Yes |

## Quick Setup for New Azure Web App

### 1. Create Azure Web App

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new Web App with Python 3.12 runtime
3. Note the **App Name** (e.g., `my-test-app-12345`)

### 2. Get Publish Profile

1. In Azure Portal, go to your Web App
2. Click **Get publish profile** in the Overview section
3. Download the `.PublishSettings` file

### 3. Configure GitHub Secrets

1. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Add a new secret with the name from `AzurePublishProfileSecret` (default: `AZURE_WEBAPP_PUBLISH_PROFILE`)
3. Paste the entire contents of the `.PublishSettings` file as the value

### 4. Update appsettings.json

Update the `DeploymentSettings` section in `python-app/appsettings.json`:

```json
{
  "DeploymentSettings": {
    "AzureWebAppName": "my-test-app-12345",
    "PythonVersion": "3.12",
    "AzurePublishProfileSecret": "AZURE_WEBAPP_PUBLISH_PROFILE",
    "Environment": "production"
  }
}
```

### 5. Deploy

Commit and push your changes to the `main` branch. The GitHub Actions workflow will automatically:

1. Read the configuration from `appsettings.json`
2. Build the app with the specified Python version
3. Deploy to the specified Azure Web App
4. Use the configured publish profile secret

## Multiple Environments

You can easily manage multiple environments by maintaining different configuration files or branches:

### Option 1: Different Configuration Files

Create environment-specific configuration files:
- `appsettings.production.json` - Production Azure Web App
- `appsettings.staging.json` - Staging Azure Web App
- `appsettings.testing.json` - Testing Azure Web App

### Option 2: Branch-Based Deployment

Use different branches with different configurations:
- `main` branch → Production deployment
- `staging` branch → Staging deployment
- `testing` branch → Testing deployment

## Workflow Behavior

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will:

1. **Read Configuration**: Extract deployment settings from `python-app/appsettings.json`
2. **Dynamic Setup**: Use the specified Python version and Azure Web App name
3. **Build**: Install dependencies and run tests with the configured Python version
4. **Security Scan**: Run security checks using the same Python version
5. **Deploy**: Deploy to the specified Azure Web App using the configured publish profile

## Troubleshooting

### Common Issues

1. **"Web App not found"**
   - Verify the `AzureWebAppName` matches your Azure Web App exactly
   - Ensure the Web App exists and is running

2. **"Authentication failed"**
   - Check that the publish profile secret is correctly configured in GitHub
   - Ensure the secret name matches `AzurePublishProfileSecret`
   - Verify the publish profile is not expired

3. **"Python version not supported"**
   - Ensure your Azure Web App supports the specified Python version
   - Check that the Python version format is correct (e.g., "3.12", not "3.12.0")

4. **"Configuration not found"**
   - Verify that `DeploymentSettings` section exists in `appsettings.json`
   - Check JSON syntax is valid

### Debugging Steps

1. **Check Workflow Logs**: Go to GitHub Actions tab and review the "Read configuration from appsettings.json" step
2. **Verify Configuration**: The workflow logs will show the parsed configuration values
3. **Test Locally**: Use the configuration test script to validate your settings
4. **Azure Portal**: Check the Azure Web App logs for deployment issues

## Example Configurations

### Development/Testing
```json
{
  "DeploymentSettings": {
    "AzureWebAppName": "accommodation-form-dev-001",
    "PythonVersion": "3.12",
    "AzurePublishProfileSecret": "AZURE_DEV_PUBLISH_PROFILE",
    "Environment": "development"
  }
}
```

### Production
```json
{
  "DeploymentSettings": {
    "AzureWebAppName": "accommodation-form-prod",
    "PythonVersion": "3.12",
    "AzurePublishProfileSecret": "AZURE_PROD_PUBLISH_PROFILE",
    "Environment": "production"
  }
}
```

## Security Considerations

- ⚠️ **Never commit publish profiles to the repository**
- ✅ Always use GitHub Secrets for sensitive information
- ✅ Use different secrets for different environments
- ✅ Regularly rotate publish profiles
- ✅ Limit branch protection to trusted contributors

## Next Steps

1. ✅ Create your Azure Web App
2. ✅ Configure GitHub Secrets
3. ✅ Update `appsettings.json`
4. ✅ Push to main branch
5. ✅ Monitor deployment in GitHub Actions
6. ✅ Verify deployment in Azure Portal

For additional help, see the main [DEPLOYMENT.md](DEPLOYMENT.md) guide or check the GitHub Actions workflow logs.