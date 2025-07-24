# API Documentation - Azure Accommodation Form Backend

This document provides comprehensive documentation for the Azure Accommodation Form backend API endpoints and usage instructions for maintainers.

## Overview

The backend provides a complete workflow for handling accommodation form submissions with the following key features:

- Email verification workflow
- Form data validation and persistence
- PDF generation with standardized naming
- Azure Blob Storage integration
- Email notifications to users and company
- Comprehensive logging and audit trails

## Architecture

### Core Components

1. **Controllers** - REST API endpoints
2. **Services** - Business logic layer
3. **Data Layer** - Entity Framework with SQL Server
4. **Models** - Data transfer objects and entities

### Technology Stack

- **.NET 8** - Framework
- **Entity Framework Core** - ORM
- **SQL Server** - Database
- **Azure Blob Storage** - File storage
- **MailKit/MimeKit** - Email services
- **iTextSharp** - PDF generation
- **Swagger** - API documentation

## API Endpoints

### Base URL
- **Development**: `https://localhost:5001`
- **Production**: `https://your-domain.com`

### Authentication
Currently no authentication is required. In production, consider implementing:
- API keys
- OAuth 2.0
- Azure AD integration

---

## Endpoint Documentation

### 1. Initialize Form Session

**POST** `/api/form/initialize`

Initializes a new form submission session and generates a unique submission ID.

#### Request Body
```json
{
  "email": "user@example.com"
}
```

#### Response
```json
{
  "submissionId": "550e8400-e29b-41d4-a716-446655440000",
  "status": 0,
  "message": "Form session initialized successfully",
  "success": true,
  "timestamp": "2025-01-20T10:30:00Z"
}
```

#### Response Codes
- `200 OK` - Success
- `400 Bad Request` - Invalid email format or missing data
- `500 Internal Server Error` - Server error

---

### 2. Send Email Verification

**POST** `/api/form/send-verification`

Sends a 6-digit verification code to the user's email address.

#### Request Body
```json
{
  "submissionId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

#### Response
```json
{
  "success": true,
  "message": "Verification email sent successfully",
  "tokenExpires": "2025-01-20T10:45:00Z"
}
```

#### Response Codes
- `200 OK` - Email sent successfully
- `400 Bad Request` - Invalid submission ID or email
- `404 Not Found` - Submission not found
- `500 Internal Server Error` - Email service error

---

### 3. Verify Email Token

**POST** `/api/form/verify-email`

Verifies the 6-digit code sent to the user's email.

#### Request Body
```json
{
  "submissionId": "550e8400-e29b-41d4-a716-446655440000",
  "token": "123456"
}
```

#### Response
```json
{
  "submissionId": "550e8400-e29b-41d4-a716-446655440000",
  "status": 2,
  "message": "Email verified successfully",
  "success": true,
  "timestamp": "2025-01-20T10:35:00Z"
}
```

#### Response Codes
- `200 OK` - Token verified successfully
- `400 Bad Request` - Invalid or expired token
- `404 Not Found` - Submission not found

---

### 4. Submit Form

**POST** `/api/form/submit`

Submits the completed form data, generates PDF, stores in blob storage, and sends confirmation emails.

#### Request Body
```json
{
  "submissionId": "550e8400-e29b-41d4-a716-446655440000",
  "formData": {
    "tenantDetails": {
      "fullName": "John Doe",
      "dateOfBirth": "1990-01-15T00:00:00Z",
      "email": "john.doe@example.com",
      // ... other form fields
    },
    "bankDetails": { /* ... */ },
    "addressHistory": [ /* ... */ ],
    // ... other form sections
  }
}
```

#### Response
```json
{
  "submissionId": "550e8400-e29b-41d4-a716-446655440000",
  "status": 5,
  "message": "Form submitted successfully",
  "success": true,
  "timestamp": "2025-01-20T10:40:00Z"
}
```

#### Response Codes
- `200 OK` - Form submitted successfully
- `400 Bad Request` - Invalid form data or email not verified
- `404 Not Found` - Submission not found
- `500 Internal Server Error` - Processing error

---

### 5. Get Submission Status

**GET** `/api/form/{submissionId}/status`

Retrieves the current status and details of a form submission (for debugging/admin purposes).

#### Response
```json
{
  "submissionId": "550e8400-e29b-41d4-a716-446655440000",
  "status": 5,
  "userEmail": "user@example.com",
  "submittedAt": "2025-01-20T10:40:00Z",
  "emailVerified": true,
  "pdfFileName": "John_Doe_Application_Form_20012025104000.pdf",
  "blobStorageUrl": "https://storage.blob.core.windows.net/...",
  "logs": [
    {
      "action": "SessionInitialized",
      "details": "Form session initialized for email: user@example.com",
      "timestamp": "2025-01-20T10:30:00Z"
    },
    // ... more log entries
  ]
}
```

---

## Status Codes Reference

### FormSubmissionStatus Enum
- `0` - **Draft** - Form session created
- `1` - **EmailSent** - Verification email sent
- `2` - **EmailVerified** - Email successfully verified
- `3` - **Submitted** - Form data submitted
- `4` - **PdfGenerated** - PDF created
- `5` - **Completed** - Process completed successfully
- `6` - **Failed** - Process failed

---

## Configuration

### Required Configuration Sections

#### appsettings.json
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=...;Database=...;Trusted_Connection=true;"
  },
  "EmailSettings": {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "SmtpUsername": "your-email@domain.com",
    "SmtpPassword": "your-app-password",
    "UseSsl": true,
    "FromEmail": "noreply@yourdomain.com",
    "FromName": "Azure Accommodation Form",
    "CompanyEmail": "company@yourdomain.com"
  },
  "BlobStorageSettings": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=...",
    "ContainerName": "form-submissions"
  },
  "ApplicationSettings": {
    "ApplicationName": "Azure Accommodation Form",
    "ApplicationUrl": "https://yourdomain.com",
    "TokenExpirationMinutes": 15,
    "TokenLength": 6
  }
}
```

---

## Deployment Instructions

### Prerequisites
1. .NET 8 Runtime
2. SQL Server database
3. Azure Storage Account
4. SMTP server access (Gmail, SendGrid, etc.)

### Steps
1. **Database Setup**
   ```bash
   dotnet ef database update
   ```

2. **Configuration**
   - Update connection strings
   - Configure email settings
   - Set blob storage credentials

3. **Build and Deploy**
   ```bash
   dotnet publish -c Release
   ```

4. **Azure App Service (Recommended)**
   - Deploy using Azure DevOps or GitHub Actions
   - Configure environment variables
   - Enable Application Insights

---

## Monitoring and Logging

### Application Insights (Recommended)
- Configure in Azure App Service
- Monitor API performance
- Track errors and exceptions

### Built-in Logging
- All operations are logged with structured logging
- Log levels: Information, Warning, Error
- Includes submission IDs for traceability

### Health Checks
Consider implementing:
- Database connectivity
- Blob storage access
- Email service availability

---

## Security Considerations

### Current Implementation
- HTTPS enforcement
- Email verification workflow
- Input validation
- SQL injection protection (EF Core)

### Production Recommendations
1. **API Authentication**
   - Implement API keys or OAuth 2.0
   - Rate limiting

2. **Data Protection**
   - Encrypt sensitive form data
   - Implement data retention policies

3. **Network Security**
   - Use Azure Private Endpoints
   - Configure firewall rules

---

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2025-01-20T10:30:00Z"
}
```

### Common Error Scenarios
1. **Invalid Email Format**
   - Status: 400
   - Message: Email validation failed

2. **Expired Verification Token**
   - Status: 400
   - Message: Verification token has expired

3. **Email Service Failure**
   - Status: 500
   - Message: Failed to send verification email

4. **Storage Service Failure**
   - Status: 500
   - Message: Failed to upload form data

---

## Development and Testing

### Local Development
1. Use LocalDB for development database
2. Configure development SMTP (MailHog recommended)
3. Use Azure Storage Emulator

### Testing Endpoints
- **Swagger UI**: Available at `/swagger` in development
- **PostMan Collection**: Can be generated from Swagger
- **Unit Tests**: Located in `Tests/` directory (if added)

### Sample cURL Commands

```bash
# Initialize form
curl -X POST "https://localhost:5001/api/form/initialize" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Send verification
curl -X POST "https://localhost:5001/api/form/send-verification" \
  -H "Content-Type: application/json" \
  -d '{"submissionId": "YOUR_ID", "email": "test@example.com"}'

# Verify email
curl -X POST "https://localhost:5001/api/form/verify-email" \
  -H "Content-Type: application/json" \
  -d '{"submissionId": "YOUR_ID", "token": "123456"}'
```

---

## Maintenance

### Regular Tasks
1. **Database Maintenance**
   - Monitor database size
   - Archive old submissions
   - Optimize indexes

2. **Storage Cleanup**
   - Implement blob lifecycle policies
   - Archive old PDF files

3. **Monitoring**
   - Review error logs
   - Monitor email delivery rates
   - Check storage usage

### Troubleshooting

#### Email Not Sending
1. Check SMTP configuration
2. Verify credentials
3. Check firewall settings
4. Review email service logs

#### PDF Generation Fails
1. Check file permissions
2. Verify iTextSharp dependencies
3. Monitor memory usage

#### Database Connection Issues
1. Check connection string
2. Verify network connectivity
3. Review SQL Server logs

---

## Support

For technical support or questions:
1. Review this documentation
2. Check application logs
3. Contact the development team
4. Create GitHub issues for bugs

---

*Last Updated: January 2025*
*Version: 1.0*