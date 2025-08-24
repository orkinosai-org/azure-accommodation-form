# Azure Accommodation Form - Python Implementation

A secure, modern web application for processing accommodation applications with certificate-based authentication, email MFA, and automated PDF generation.

## Configuration Migration from .NET

This Python application now mirrors the complete configuration structure from the .NET Blazor application's `appsettings.json`. All settings have been implemented with Python equivalents while maintaining backward compatibility.

### ✅ Implemented Configuration Sections

- **Logging Configuration** - Complete .NET log level mapping (TRACE→DEBUG, INFORMATION→INFO, etc.)
- **Email Settings** - Full SMTP configuration mirroring .NET EmailSettings
- **Azure Blob Storage** - Complete BlobStorageSettings equivalent
- **Application Settings** - Application metadata and token configuration
- **Application Insights** - Telemetry and monitoring integration
- **Diagnostics** - Retention policies and logging settings

### 📋 Configuration Mapping

| .NET Section | Python Equivalent | Status |
|--------------|-------------------|--------|
| `Logging.LogLevel` | `LoggingSettings` | ✅ Complete |
| `EmailSettings` | `EmailSettings` | ✅ Complete |
| `BlobStorageSettings` | `BlobStorageSettings` | ✅ Complete |
| `ApplicationSettings` | `ApplicationSettings` | ✅ Complete |
| `ApplicationInsights` | `ApplicationInsightsSettings` | ✅ Complete |
| `Diagnostics` | `DiagnosticsSettings` | ✅ Complete |
| `AllowedHosts` | FastAPI middleware | ⚠️ Different implementation |
| `ConnectionStrings.DefaultConnection` | N/A | ❌ Not needed (no database) |

## Features

- **Certificate-based authentication** for secure access
- **Multi-factor authentication** via email verification
- **CAPTCHA protection** against spam and automated submissions
- **Professional PDF generation** with automated naming
- **Azure Blob Storage** integration for secure file storage
- **Email notifications** to both users and administrators
- **Application Insights** telemetry and monitoring
- **Real-time form validation** and user-friendly interface
- **Admin dashboard** for submission management
- **Comprehensive logging** with .NET-compatible log levels

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Configuration**: Pydantic Settings with .NET appsettings.json structure
- **Frontend**: Modern JavaScript with Bootstrap 5
- **PDF Generation**: ReportLab for professional documents
- **Email**: SMTP with HTML templates (mirrors .NET EmailSettings)
- **Storage**: Azure Blob Storage (mirrors .NET BlobStorageSettings)
- **Telemetry**: Application Insights integration
- **Authentication**: Certificate-based with session management

## Quick Start

### 1. Installation

```bash
cd python-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

The application uses an `appsettings.json` file that mirrors the .NET Blazor application structure. 

**Automatic Setup (Recommended):**
Simply run the application and it will automatically create `appsettings.json` from the example template if it doesn't exist.

**Manual Setup:**
```bash
cp appsettings.example.json appsettings.json
# Edit appsettings.json with your configuration
```

**Required settings:**
- Email/SMTP configuration (mirrors .NET EmailSettings)
- Azure Blob Storage connection (mirrors .NET BlobStorageSettings)  
- Application Insights connection (mirrors .NET ApplicationInsights)
- Logging levels (mirrors .NET Logging.LogLevel)

See [APPSETTINGS_JSON_GUIDE.md](APPSETTINGS_JSON_GUIDE.md) for complete configuration guide.

### 3. Run Development Server

```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Configuration

### Email Settings

Configure SMTP for email delivery in `appsettings.json`:

```json
{
  "EmailSettings": {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "SmtpUsername": "your-email@gmail.com",
    "SmtpPassword": "your-app-password",
    "UseSsl": true,
    "FromEmail": "noreply@yourdomain.com",
    "FromName": "Azure Accommodation Form",
    "CompanyEmail": "admin@yourdomain.com"
  }
}
```

### Azure Blob Storage

Set up Azure Blob Storage for PDF storage in `appsettings.json`:

```json
{
  "BlobStorageSettings": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=youracccount;AccountKey=yourkey;EndpointSuffix=core.windows.net",
    "ContainerName": "form-submissions"
  }
}
```

### Application Insights

Configure monitoring and telemetry in `appsettings.json`:

```json
{
  "ApplicationInsights": {
    "ConnectionString": "InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/"
  }
}
```
CAPTCHA_SECRET_KEY=your-secret-key
```

### SSL/TLS (Production)

For production deployment with HTTPS:

```env
SSL_KEYFILE=/path/to/private.key
SSL_CERTFILE=/path/to/certificate.crt
```

## Azure Deployment

### Automated GitHub Actions Deployment

The application includes automated deployment to Azure Web Apps via GitHub Actions. The deployment configuration is managed through `appsettings.json`:

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

### Quick Deployment Setup

1. **Create Azure Web App** with Python 3.12 runtime
2. **Download publish profile** from Azure Portal
3. **Add GitHub Secret** with your publish profile content
4. **Update appsettings.json** with your Azure Web App name
5. **Push to main branch** - deployment happens automatically!

📖 **See [AZURE_DEPLOYMENT_CONFIG.md](AZURE_DEPLOYMENT_CONFIG.md) for detailed deployment configuration guide**

### Multiple Environment Support

Easily deploy to different Azure Web Apps by updating the `DeploymentSettings` section:
- ✅ Development/Testing environments
- ✅ Staging environments  
- ✅ Production environments
- ✅ Automatic Python 3.12 runtime configuration
- ✅ Environment-specific secrets management

## API Endpoints

### Authentication
- `POST /api/auth/verify-certificate` - Verify client certificate
- `POST /api/auth/request-email-verification` - Request email MFA
- `POST /api/auth/verify-mfa-token` - Verify MFA token
- `GET /api/auth/session/status` - Check session status

### Form Processing
- `POST /api/form/initialize` - Initialize form session
- `POST /api/form/submit` - Submit completed form
- `GET /api/form/submission/{id}/status` - Get submission status
- `GET /api/form/download/{id}` - Download user's PDF

### Admin (Requires Admin Token)
- `GET /api/admin/submissions` - List all submissions
- `GET /api/admin/submissions/{id}` - Get submission details
- `GET /api/admin/submissions/{id}/download` - Download submission PDF
- `POST /api/admin/submissions/{id}/resend-email` - Resend confirmation email
- `GET /api/admin/stats` - Get statistics
- `DELETE /api/admin/submissions/{id}` - Delete submission
- `GET /api/admin/config/email` - Get email configuration
- `POST /api/admin/config/email/test` - Send test email

#### Admin Logging Endpoints
- `GET /api/admin/logs` - View recent application logs
- `GET /api/admin/logs/levels` - Get current log levels for all loggers
- `POST /api/admin/logs/levels` - Update log level for a specific logger
- `GET /api/admin/logs/download` - Download application logs as file (txt/json)
- `POST /api/admin/logs/clear` - Clear the in-memory log cache

## Form Schema

The application processes accommodation forms with the following sections:

1. **Tenant Details** - Personal information, contact details
2. **Bank Details** - Banking information for payments
3. **Address History** - 3-year address history
4. **Emergency Contact** - Next of kin information
5. **Medical Details** - GP and medical information
6. **Employment** - Current employment details
7. **Passport Details** - Identity verification
8. **Current Living** - Current accommodation details
9. **Other Details** - Pets, smoking, preferences
10. **Agreements** - Occupation terms and conditions
11. **Consent & Declaration** - Legal consent and declarations

## PDF Generation

Generated PDFs include:
- All form data in a professional layout
- Secure naming: `FirstName_LastName_Application_Form_DDMMYYYYHHMM.pdf`
- Client IP and submission timestamps
- Digital signatures (typed or drawn)

## Security Features

- **Certificate Authentication**: Validates client certificates
- **Email MFA**: 6-digit verification codes with expiry
- **CAPTCHA**: Prevents automated submissions
- **Session Management**: Secure token-based sessions
- **Input Validation**: Comprehensive data validation
- **Rate Limiting**: Prevents abuse and spam
- **Audit Logging**: Complete audit trail

## Deployment

### Azure App Service

1. **Create App Service**:
   ```bash
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myapp --runtime "PYTHON|3.11"
   ```

2. **Configure Environment Variables**:
   Set all required environment variables in Azure App Service configuration.

3. **Deploy Code**:
   ```bash
   az webapp deployment source config --name myapp --resource-group myResourceGroup --repo-url https://github.com/yourusername/yourrepo --branch main
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## Development

### Project Structure

```
python-app/
├── app/
│   ├── api/              # API route handlers
│   ├── core/             # Core configuration and security
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic services
│   ├── static/           # CSS, JavaScript, images
│   └── templates/        # HTML templates
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── .env.example         # Environment configuration template
```

### Adding New Form Fields

1. Update the Pydantic models in `app/models/form.py`
2. Modify the PDF generation in `app/services/pdf.py`
3. Update the frontend form in `app/static/js/app.js`
4. Add validation rules as needed

### Customizing Branding

1. **Logo**: Replace files in `app/static/images/`
2. **Colors**: Update CSS variables in `app/static/css/style.css`
3. **Email Templates**: Modify templates in `app/services/email.py`
4. **Text Content**: Update templates in `app/templates/`

## Monitoring

The application includes:
- Health check endpoint: `/health`
- Comprehensive logging to console
- Session tracking and cleanup
- Error handling and reporting

## Testing

```bash
# Run with development settings
ENVIRONMENT=development python main.py

# Test API endpoints
curl -X POST http://localhost:8000/api/auth/verify-certificate

# Check health
curl http://localhost:8000/health
```

## Support

For issues and questions:
1. Check the logs for error details
2. Verify configuration settings
3. Test connectivity to external services
4. Review the API documentation at `/docs` (development mode)

## License

This project is licensed under the MIT License. See LICENSE file for details.