# Azure Accommodation Application Form

This project provides a secure, user-friendly web application for accommodation applications, built with **Python (FastAPI)**.

## Project Goals

- Replace paper/email form submission with a secure web app.
- Automate authentication, MFA, and PDF generation.
- Store submissions securely and send confirmations via email.
- Fit the workflow described in the [docs/requirements.md](docs/requirements.md).

## Implementation

### Python FastAPI Backend
Modern, high-performance Python web framework with automatic API documentation.

**Features:**
- Fast, modern Python web framework
- Automatic API documentation with OpenAPI/Swagger
- Built-in validation with Pydantic models
- **Complete backend API for form processing**
- **PDF generation using ReportLab**
- **SMTP email integration**
- **Azure Blob Storage integration**
- Ready for Azure App Service deployment

**Setup:**
```bash
cd python-app
pip install -r requirements.txt
python main.py
```
The app will be available at [http://localhost:8000](http://localhost:8000)

📖 See [python-app/README.md](python-app/README.md) for implementation details.

## Backend API

The Python implementation includes a complete backend API that processes form submissions by:

1. **Receiving form data** via RESTful API endpoints
2. **Generating PDF** from submitted form data using ReportLab
3. **Sending PDF via SMTP email** to both the user and admin
4. **Saving PDF to Azure Blob Storage** for archival
5. **Logging all operations** with comprehensive error handling

### API Endpoints

- `POST /submit-form` - Submit form directly
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Configuration

The backend can be configured via `appsettings.json` or environment variables:

#### SMTP Settings
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

#### Azure Blob Storage Settings
```json
{
  "BlobStorageSettings": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net",
    "ContainerName": "form-submissions"
  }
}
```

#### Environment Variables
All settings can be overridden using environment variables:
- `SMTP_SERVER`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `COMPANY_EMAIL`
- `AZURE_STORAGE_CONNECTION_STRING`

### Usage Example

**Direct Form Submission:**
```bash
curl -X POST https://your-app.azurewebsites.net/submit-form \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_details": {
      "full_name": "John Doe",
      "email": "john@example.com",
      "telephone": "+1234567890",
      "date_of_birth": "1990-01-01"
    },
    "bank_details": { ... },
    "address_history": [ ... ],
    ...
  }'
```

**Response:**
```json
{
  "submission_id": "12345678-1234-1234-1234-123456789012",
  "status": "success",
  "message": "Form submitted and processed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Technology Stack

### Python Implementation
- **Backend:** FastAPI with Pydantic models for validation
- **PDF Generation:** ReportLab
- **Email:** SMTP integration
- **Storage:** Azure Blob Storage
- **Database:** JSON-based storage with Azure integration
- **Hosting:** Azure App Service
- **Documentation:** Automatic OpenAPI/Swagger generation

## Form Structure

The application provides identical functionality across all sections:

✅ **12 Form Sections:**
1. Tenant Details
2. Bank Details
3. Address History (3 years)
4. Contacts  
5. Medical Details
6. Employment
7. Employment Change
8. Passport Details
9. Current Living Arrangement
10. Other Details
11. Occupation Agreement
12. Consent & Declaration

✅ **Interactive Features:**
- Conditional field visibility
- Dynamic address history addition
- Form validation and submission
- JSON serialization for backend processing

## Available Scripts

### Python (FastAPI)
- `python main.py` - Start the development server
- `uvicorn main:app --reload` - Start with auto-reload for development
- `pytest tests/` - Run tests
- `gunicorn main:app` - Production server with Gunicorn

## Project Structure

```
./
├── python-app/                   # Python FastAPI implementation
│   ├── app/
│   │   ├── models/              # Pydantic models
│   │   ├── services/            # Business logic services
│   │   └── utils/               # Utility functions
│   ├── tests/                   # Test files
│   ├── main.py                  # Application entry point
│   ├── requirements.txt         # Python dependencies
│   ├── appsettings.json         # Configuration
│   └── README.md               # Python app documentation
├── docs/                        # Documentation
│   ├── requirements.md          # Project requirements
│   └── form_fields.md          # Form structure details
└── form_schema.json            # JSON schema for form data
```

### GitHub Actions Workflows

- **`deploy.yml`** - Python app deployment
- **`main_testapp.yml`** - Test app deployment

## Backend Integration

The form generates JSON data that is processed by the Python backend:

```json
{
  "tenant_details": {
    "full_name": "...",
    "email": "...",
    // ... other fields
  },
  "bank_details": { ... },
  "address_history": [ ... ],
  // ... other sections
}
```

## Developer Notes

- See [docs/form_fields.md](docs/form_fields.md) for the complete form structure
- The form schema is defined in [form_schema.json](form_schema.json)
- For Python-specific details, see [python-app/README.md](python-app/README.md)
- **No database dependency for form data** - submissions are stored as JSON and archived as PDFs in Azure Blob Storage

## Deployment

Deploy to Azure App Service with Python 3.12 runtime. The application includes comprehensive logging and error handling.

### Manual Deployment

**Required Configuration:**
1. Set up Azure Blob Storage account
2. Configure SMTP email settings (Gmail, Outlook, or custom SMTP)
3. Set environment variables for production secrets
4. Update `appsettings.json` or use Azure App Service configuration

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step deployment instructions.**

## Security & Privacy

- **No sensitive data stored in database** - only submission metadata and logs
- **PDF files encrypted in transit and at rest** in Azure Blob Storage
- **Comprehensive logging** for audit trails
- **Configuration via environment variables** for secure secret management

## Branding

If you have branding assets, place them in the `branding/` folder.

---

**Getting Started:**
1. Follow the setup instructions above
2. Configure SMTP and Azure Blob Storage settings in `appsettings.json`
3. Customize the form fields and styling as needed
4. Deploy to Azure