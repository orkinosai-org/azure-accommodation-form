# Azure Accommodation Form – Python Deployment Guide

Welcome! This guide will help you deploy the Azure Accommodation Form Python application to your Azure subscription.

---

## 1. Prerequisites

- An **Azure subscription**
- **Azure App Service** ready for Python 3.12 (see below)
- [Git](https://git-scm.com/downloads) installed
- [Python 3.12](https://www.python.org/downloads/) installed locally (for testing/building)
- [Visual Studio Code](https://code.visualstudio.com/) or your preferred editor

---

## 2. Setting Up Your Azure Web App

### Option 1: Create a New Web App for Python

1. Go to the [Azure Portal](https://portal.azure.com/).
2. Click `Create a resource > Web App`.
3. Set the **Runtime stack** to `Python 3.12`.
4. Finish the wizard and note your App Service name.

### Option 2: Change an Existing Web App to Python

1. In the Azure Portal, go to your App Service.
2. Under `Settings`, click `Configuration > General settings`.
3. Change `Stack` to `Python` and `Version` to `3.12`.
4. Save and restart the app.

> **Note:** Changing the stack removes any previous .NET/Blazor functionality.

---

## 3. Cloning the Repository

1. Open a terminal and run:
   ```bash
   git clone https://github.com/orkinosai-org/azure-accommodation-form.git
   cd azure-accommodation-form
   ```

---

## 4. Local Setup and Testing

1. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r deployments/requirements.txt
   ```

3. Run your app locally (update as needed for your framework, e.g., FastAPI):
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

---

## 5. Preparing for Deployment

- Ensure your app's entry point is named as expected (e.g., `app.py` with a variable `app` for ASGI).
- Update `requirements.txt` as needed.
- If custom startup is required, edit `deployments/startup.sh`.

---

## 6. Deploying to Azure

### Option A: ZIP Deploy

1. Zip your application files (excluding `venv` and other local/dev files).
2. Go to Azure Portal > Your App Service > Deployment Center.
3. Choose `ZIP Deploy` and upload your zipped package.

### Option B: GitHub Actions (Manual Trigger)

- You can manually trigger a build and deployment using the included GitHub Actions workflow:
    - Go to the repo on GitHub.
    - Click on `Actions` tab > `Manual Deploy` workflow.
    - Click `Run workflow` and follow the prompts.

---

## 7. Configuration Setup

**Recommended approach:** Use the pre-built deployment packages:
- `/deployment_package/` - Includes `appsettings.json` with clear placeholder values
- `/azure-deployment-package/` - Alternative deployment package with same structure

Simply edit the `appsettings.json` file with your settings before deploying.

**Alternative approach for advanced users:**
- Set configuration via Azure Portal > App Service > Configuration > Application settings.
- Never commit secrets to the repository.

---

## 8. Additional Notes

- If your app uses a database or storage, provision those in Azure and update connection strings.
- Check Azure App Service logs for troubleshooting.

---

Thank you for using Azure Accommodation Form!