# Azure Accommodation Application Form

This project provides a secure, user-friendly web application for accommodation applications, built with **Blazor (.NET 8 LTS)**.

## 📦 Quick Deployment

**For clients who want to deploy the application:**

```bash
# Create a deployment package with safe configuration
./build_deployment_package.sh
# or
python3 create_deployment_package.py
```

This creates `deployment_package.zip` containing:
- ✅ Ready-to-deploy application files
- ✅ Safe configuration templates (no real secrets)
- ✅ Client-friendly setup instructions
- ✅ Both Blazor (.NET 8) and Python implementations

The package includes detailed instructions for editing configuration files and deploying to Azure.

## Project Goals

- Replace paper/email form submission with a secure web app.
- Automate authentication, MFA, and PDF generation.
- Store submissions securely and send confirmations via email.
- Fit the workflow described in the [docs/requirements.md](docs/requirements.md).

## Implementation

### Blazor Server (.NET 8 LTS)
Modern server-side implementation with interactive components and **full backend API**.

**Features:**
- Server-side rendering for better performance and SEO
- Interactive server components via SignalR
- Built-in validation with C# models
- Type-safe development with .NET
- **Complete backend API for form processing**
- **PDF generation using QuestPDF**
- **SMTP email integration with MailKit**
- **Azure Blob Storage integration**
- Ready for Azure App Service deployment

**Setup:**
```bash
cd BlazorApp
dotnet restore
dotnet build  
dotnet run
```
The app will be available at [http://localhost:5260](http://localhost:5260)

📖 See [BlazorApp/MIGRATION.md](BlazorApp/MIGRATION.md) for implementation details.

## Backend API

The Blazor implementation includes a complete backend API that processes form submissions by:

1. **Receiving form data** via RESTful API endpoints
2. **Generating PDF** from submitted form data using QuestPDF
3. **Sending PDF via SMTP email** to both the user and admin
4. **Saving PDF to Azure Blob Storage** for archival
5. **Logging all operations** with comprehensive error handling

### API Endpoints

- `POST /api/form/initialize` - Initialize a new form session
- `POST /api/form/send-verification` - Send email verification token
- `POST /api/form/verify-email` - Verify email using token
- `POST /api/form/submit` - Submit form (requires email verification)
- `POST /api/form/submit-direct` - Submit form directly (no email verification required)
- `GET /api/form/{submissionId}/status` - Get submission status

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
- `EmailSettings__SmtpServer`
- `EmailSettings__SmtpUsername`
- `EmailSettings__SmtpPassword`
- `EmailSettings__CompanyEmail`
- `BlobStorageSettings__ConnectionString`
- `BlobStorageSettings__ContainerName`

### Usage Example

**Direct Form Submission:**
```bash
curl -X POST https://your-app.azurewebsites.net/api/form/submit-direct \
  -H "Content-Type: application/json" \
  -d '{
    "tenantDetails": {
      "fullName": "John Doe",
      "email": "john@example.com",
      "telephone": "+1234567890",
      "dateOfBirth": "1990-01-01"
    },
    "bankDetails": { ... },
    "addressHistory": [ ... ],
    ...
  }'
```

**Response:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "status": "Completed",
  "message": "Form submitted and processed successfully",
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Technology Stack

### Blazor Implementation
- **Frontend:** Blazor Server with Interactive Server Components
- **Backend:** .NET 8, C# models with validation attributes  
- **PDF Generation:** QuestPDF
- **Email:** MailKit/MimeKit for SMTP
- **Storage:** Azure Blob Storage
- **Database:** Entity Framework Core (SQLite dev, SQL Server prod)
- **Hosting:** Azure App Service
- **Real-time:** SignalR for interactive features

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

### Blazor (.NET 8)
- `dotnet run` - Start the development server
- `dotnet build` - Build the application
- `dotnet test` - Run tests (if any)
- `dotnet publish` - Build for production deployment

## Project Structure

```
./
├── BlazorApp/                    # .NET 8 Blazor implementation
│   ├── Components/
│   │   ├── Pages/Home.razor     # Main form component
│   │   └── Layout/              # Layout components
│   ├── Controllers/
│   │   └── FormController.cs    # API endpoints
│   ├── Services/
│   │   ├── FormService.cs       # Form processing logic
│   │   ├── PdfGenerationService.cs # QuestPDF integration
│   │   ├── EmailService.cs      # SMTP email service
│   │   └── BlobStorageService.cs # Azure Blob Storage
│   ├── Models/FormModels.cs     # C# form models with validation
│   ├── Data/ApplicationDbContext.cs # Entity Framework context
│   ├── Program.cs               # Application entry point
│   ├── appsettings.json         # Development configuration
│   ├── appsettings.Example.json # Production configuration example
│   └── MIGRATION.md             # Migration documentation
├── docs/                        # Documentation
│   ├── requirements.md          # Project requirements
│   └── form_fields.md          # Form structure details
└── form_schema.json            # JSON schema for form data
```

### GitHub Actions Workflows

- **`build-deployment-package.yml`** - Automated deployment package creation
- **`deploy.yml`** - Python app deployment (existing)  
- **`main_testapp.yml`** - Test app deployment (existing)

## Backend Integration

The form generates JSON data that is processed by the Blazor backend:

```json
{
  "TenantDetails": {
    "FullName": "...",
    "Email": "...",
    // ... other fields
  },
  "BankDetails": { ... },
  "AddressHistory": [ ... ],
  // ... other sections
}
```

## Developer Notes

- See [docs/form_fields.md](docs/form_fields.md) for the complete form structure
- The form schema is defined in [form_schema.json](form_schema.json)
- For Blazor-specific details, see [BlazorApp/MIGRATION.md](BlazorApp/MIGRATION.md)
- **No database dependency for form data** - submissions are stored as JSON and archived as PDFs in Azure Blob Storage
- Entity Framework is used only for tracking submission status and logs

## Deployment

Deploy to Azure App Service with .NET 8 runtime. The application includes SignalR support for interactive features.

### Automated Deployment Package Creation

The repository includes a GitHub Actions workflow that automatically creates deployment-ready packages on each push to main:

1. **Triggers automatically** on push to main branch
2. **Builds both applications** (Blazor and Python) for production
3. **Creates deployment package** with configuration templates
4. **Generates ZIP file** for easy client transfer
5. **Available as artifact** from GitHub Actions runs

**To use the deployment package:**
1. Navigate to Actions tab in GitHub
2. Find latest "Build Deployment Package" workflow run
3. Download the `deployment-package-zip` artifact
4. Follow instructions in `DEPLOYMENT.md` for Azure setup

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
- **Email verification** ensures form submissions are from valid email addresses
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