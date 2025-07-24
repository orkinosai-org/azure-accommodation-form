# Azure Accommodation Form - Usage Instructions

## Quick Start

This guide will help you set up and configure the Azure Accommodation Form backend API for processing form submissions.

## Prerequisites

- .NET 8 SDK
- Azure Storage Account (for blob storage)
- SMTP server credentials (Gmail, Outlook, or custom)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/orkinosai-org/azure-accommodation-form.git
   cd azure-accommodation-form/BlazorApp
   ```

2. **Restore dependencies:**
   ```bash
   dotnet restore
   ```

3. **Build the application:**
   ```bash
   dotnet build
   ```

## Configuration

### 1. SMTP Email Settings

Configure your SMTP server settings in `appsettings.json`:

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

**For Gmail:**
- Use App Passwords instead of your regular password
- Enable 2-factor authentication
- Generate an App Password from Google Account settings

**For Outlook/Hotmail:**
- Use App Passwords if 2FA is enabled
- SMTP server: `smtp-mail.outlook.com`, Port: `587`

### 2. Azure Blob Storage

Configure Azure Blob Storage for PDF archival:

```json
{
  "BlobStorageSettings": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=your-storage-key;EndpointSuffix=core.windows.net",
    "ContainerName": "form-submissions"
  }
}
```

**To get Azure Storage credentials:**
1. Go to Azure Portal
2. Create or select a Storage Account
3. Go to "Access keys" section
4. Copy the connection string

### 3. Environment Variables (Production)

For production deployment, use environment variables instead of storing secrets in config files:

```bash
export EmailSettings__SmtpUsername="your-email@gmail.com"
export EmailSettings__SmtpPassword="your-app-password"
export EmailSettings__CompanyEmail="admin@yourdomain.com"
export BlobStorageSettings__ConnectionString="your-azure-storage-connection-string"
```

## Running the Application

### Development
```bash
dotnet run
```
The application will be available at:
- HTTPS: https://localhost:5001
- HTTP: http://localhost:5000
- API Documentation: https://localhost:5001/swagger

### Production
```bash
dotnet publish -c Release -o ./publish
cd publish
dotnet BlazorApp.dll
```

## Testing the API

### 1. Test Direct Form Submission

```bash
curl -X POST https://localhost:5001/api/form/submit-direct \
  -H "Content-Type: application/json" \
  -d '{
    "tenantDetails": {
      "fullName": "John Doe",
      "email": "john@example.com",
      "telephone": "+1234567890",
      "dateOfBirth": "1990-01-01",
      "rightToLiveInUk": true
    },
    "bankDetails": {
      "bankName": "Example Bank",
      "accountNo": "12345678",
      "sortCode": "12-34-56",
      "postcode": "SW1A 1AA"
    },
    "addressHistory": [
      {
        "address": "123 Main St, London, UK",
        "from": "2020-01-01",
        "to": "2023-12-31",
        "landlordName": "John Smith",
        "landlordTel": "+1234567890",
        "landlordEmail": "landlord@example.com"
      }
    ],
    "contacts": {
      "nextOfKin": "Jane Doe",
      "relationship": "Sister",
      "address": "456 Oak Ave, London, UK",
      "contactNumber": "+1234567891"
    },
    "medicalDetails": {
      "gpPractice": "City Health Centre",
      "doctorName": "Dr. Smith",
      "doctorAddress": "789 Health St, London, UK",
      "doctorTelephone": "+1234567892"
    },
    "employment": {
      "employerName": "Tech Company Ltd",
      "employerAddress": "321 Business Park, London, UK",
      "jobTitle": "Software Developer",
      "managerName": "Alice Johnson",
      "managerTel": "+1234567893",
      "managerEmail": "alice@techcompany.com",
      "dateOfEmployment": "2020-01-01",
      "presentSalary": "£50,000"
    },
    "employmentChange": "No changes expected",
    "passportDetails": {
      "passportNumber": "123456789",
      "dateOfIssue": "2020-01-01",
      "placeOfIssue": "London"
    },
    "currentLivingArrangement": {
      "landlordKnows": true,
      "noticeEndDate": "2024-02-01",
      "reasonLeaving": "Moving closer to work",
      "landlordReference": true,
      "landlordContact": {
        "name": "Current Landlord",
        "address": "Current Address",
        "tel": "+1234567894",
        "email": "current@landlord.com"
      }
    },
    "other": {
      "pets": {
        "hasPets": false,
        "details": ""
      },
      "smoke": false,
      "coliving": {
        "hasColiving": false,
        "details": ""
      }
    },
    "occupationAgreement": {
      "singleOccupancyAgree": true,
      "hmoTermsAgree": true,
      "noUnlistedOccupants": true,
      "noSmoking": true,
      "kitchenCookingOnly": true
    },
    "consentAndDeclaration": {
      "consentGiven": true,
      "signature": "John Doe",
      "date": "2024-01-15",
      "printName": "John Doe",
      "declaration": {
        "mainHome": true,
        "enquiriesPermission": true,
        "certifyNoJudgements": true,
        "certifyNoHousingDebt": true,
        "certifyNoLandlordDebt": true,
        "certifyNoAbuse": true
      },
      "declarationSignature": "John Doe",
      "declarationDate": "2024-01-15",
      "declarationPrintName": "John Doe"
    }
  }'
```

### 2. Check Submission Status

```bash
curl https://localhost:5001/api/form/{submissionId}/status
```

## Azure Deployment

### 1. Deploy to Azure App Service

1. **Create App Service:**
   - Go to Azure Portal
   - Create new App Service
   - Select .NET 8 runtime stack

2. **Configure App Settings:**
   - Add all EmailSettings and BlobStorageSettings as Application Settings
   - Use double underscores for nested settings (e.g., `EmailSettings__SmtpServer`)

3. **Deploy:**
   ```bash
   # Using Azure CLI
   az webapp deployment source config-zip --resource-group myResourceGroup --name myapp --src publish.zip
   
   # Or publish directly from Visual Studio/VS Code
   ```

### 2. Environment Variables for Azure

Set these in Azure App Service Configuration:

- `EmailSettings__SmtpServer` = `smtp.gmail.com`
- `EmailSettings__SmtpPort` = `587`
- `EmailSettings__SmtpUsername` = `your-email@gmail.com`
- `EmailSettings__SmtpPassword` = `your-app-password`
- `EmailSettings__FromEmail` = `noreply@yourdomain.com`
- `EmailSettings__CompanyEmail` = `admin@yourdomain.com`
- `BlobStorageSettings__ConnectionString` = `your-azure-storage-connection-string`
- `BlobStorageSettings__ContainerName` = `form-submissions`

## Troubleshooting

### Common Issues

1. **Email not sending:**
   - Check SMTP credentials
   - Verify App Password for Gmail
   - Check firewall/network restrictions

2. **Blob storage errors:**
   - Verify connection string
   - Check storage account permissions
   - Ensure container exists (it's created automatically)

3. **PDF generation fails:**
   - Check QuestPDF license (Community license is free)
   - Verify form data structure

4. **Build errors:**
   - Ensure .NET 8 SDK is installed
   - Run `dotnet restore` to restore packages

### Logs

Check application logs for detailed error information:

```bash
# Development
dotnet run --verbosity detailed

# Production (Azure)
# Check Application Insights or App Service logs in Azure Portal
```

## Security Considerations

1. **Never commit secrets** to source control
2. **Use environment variables** for production secrets
3. **Enable HTTPS** in production
4. **Restrict CORS** policies as needed
5. **Monitor access logs** for suspicious activity

## Support

For issues and questions:
1. Check the logs for error details
2. Verify configuration settings
3. Test API endpoints individually
4. Refer to API_DOCUMENTATION.md for detailed endpoint specs