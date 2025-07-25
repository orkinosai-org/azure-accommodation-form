# Azure Accommodation Form API Documentation

## Overview

The Azure Accommodation Form API provides endpoints for processing accommodation form submissions. The API handles the complete workflow from form submission to PDF generation, email notifications, and Azure Blob Storage archival.

## Base URL

- Development: `https://localhost:5001`
- Production: `https://your-app.azurewebsites.net`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Endpoints

### 1. Initialize Form Session

Initialize a new form submission session.

**Endpoint:** `POST /api/form/initialize`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "status": "Draft",
  "message": "Form session initialized successfully",
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Send Email Verification

Send a verification token to the user's email address.

**Endpoint:** `POST /api/form/send-verification`

**Request Body:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification email sent successfully",
  "tokenExpires": "2024-01-15T10:45:00Z"
}
```

### 3. Verify Email Token

Verify the email using the token sent to the user.

**Endpoint:** `POST /api/form/verify-email`

**Request Body:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "token": "123456"
}
```

**Response:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "status": "EmailVerified",
  "message": "Email verified successfully",
  "success": true,
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### 4. Submit Form (with Email Verification)

Submit the form data after email verification.

**Endpoint:** `POST /api/form/submit`

**Request Body:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "formData": {
    "tenantDetails": {
      "fullName": "John Doe",
      "dateOfBirth": "1990-01-01",
      "email": "john@example.com",
      "telephone": "+1234567890",
      // ... other tenant details
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
    // ... other form sections
  }
}
```

**Response:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "status": "Completed",
  "message": "Form submitted successfully",
  "success": true,
  "timestamp": "2024-01-15T10:40:00Z"
}
```

### 5. Submit Form Directly (No Email Verification)

Submit form data directly without email verification workflow.

**Endpoint:** `POST /api/form/submit-direct`

**Request Body:**
```json
{
  "tenantDetails": {
    "fullName": "John Doe",
    "dateOfBirth": "1990-01-01",
    "email": "john@example.com",
    "telephone": "+1234567890",
    // ... other tenant details
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
  // ... other form sections
}
```

**Response:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "status": "Completed",
  "message": "Form submitted and processed successfully",
  "success": true,
  "timestamp": "2024-01-15T10:40:00Z"
}
```

### 6. Get Submission Status

Get the current status and details of a form submission.

**Endpoint:** `GET /api/form/{submissionId}/status`

**Response:**
```json
{
  "submissionId": "12345678-1234-1234-1234-123456789012",
  "status": "Completed",
  "userEmail": "user@example.com",
  "submittedAt": "2024-01-15T10:40:00Z",
  "emailVerified": true,
  "pdfFileName": "John_Doe_Application_Form_15012024_1040.pdf",
  "blobStorageUrl": "https://yourstorageaccount.blob.core.windows.net/form-submissions/12345678-1234-1234-1234-123456789012/John_Doe_Application_Form_15012024_1040.pdf",
  "logs": [
    {
      "action": "SessionInitialized",
      "details": "Form session initialized for email: user@example.com",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "action": "EmailVerificationSent",
      "details": "Verification token sent to user@example.com",
      "timestamp": "2024-01-15T10:31:00Z"
    },
    {
      "action": "EmailVerified",
      "details": "Email successfully verified",
      "timestamp": "2024-01-15T10:35:00Z"
    },
    {
      "action": "FormSubmitted",
      "details": "Form data submitted successfully",
      "timestamp": "2024-01-15T10:40:00Z"
    },
    {
      "action": "PdfGenerated",
      "details": "PDF generated: John_Doe_Application_Form_15012024_1040.pdf",
      "timestamp": "2024-01-15T10:40:00Z"
    },
    {
      "action": "PdfUploaded",
      "details": "PDF uploaded to: https://yourstorageaccount.blob.core.windows.net/...",
      "timestamp": "2024-01-15T10:40:00Z"
    },
    {
      "action": "EmailsSent",
      "details": "Confirmation emails sent successfully",
      "timestamp": "2024-01-15T10:40:00Z"
    }
  ]
}
```

## Form Data Structure

### Complete Form Schema

The form data follows this structure:

```json
{
  "tenantDetails": {
    "fullName": "string (required)",
    "dateOfBirth": "string (YYYY-MM-DD)",
    "placeOfBirth": "string",
    "email": "string (required, email format)",
    "telephone": "string (required, phone format)",
    "employersName": "string",
    "gender": "Male | Female",
    "niNumber": "string",
    "car": "boolean",
    "bicycle": "boolean",
    "rightToLiveInUk": "boolean",
    "otherNames": {
      "hasOtherNames": "boolean",
      "details": "string"
    },
    "roomOccupancy": "JustYou | YouAndSomeoneElse",
    "medicalCondition": {
      "hasCondition": "boolean",
      "details": "string"
    }
  },
  "bankDetails": {
    "bankName": "string",
    "postcode": "string",
    "accountNo": "string",
    "sortCode": "string"
  },
  "addressHistory": [
    {
      "address": "string",
      "from": "string (YYYY-MM-DD)",
      "to": "string (YYYY-MM-DD)",
      "landlordName": "string",
      "landlordTel": "string (phone format)",
      "landlordEmail": "string (email format)"
    }
  ],
  "contacts": {
    "nextOfKin": "string",
    "relationship": "string",
    "address": "string",
    "contactNumber": "string (phone format)"
  },
  "medicalDetails": {
    "gpPractice": "string",
    "doctorName": "string",
    "doctorAddress": "string",
    "doctorTelephone": "string (phone format)"
  },
  "employment": {
    "employerName": "string",
    "employerAddress": "string",
    "jobTitle": "string",
    "managerName": "string",
    "managerTel": "string (phone format)",
    "managerEmail": "string (email format)",
    "dateOfEmployment": "string (YYYY-MM-DD)",
    "presentSalary": "string"
  },
  "employmentChange": "string",
  "passportDetails": {
    "passportNumber": "string",
    "dateOfIssue": "string (YYYY-MM-DD)",
    "placeOfIssue": "string"
  },
  "currentLivingArrangement": {
    "landlordKnows": "boolean",
    "noticeEndDate": "string (YYYY-MM-DD)",
    "reasonLeaving": "string",
    "landlordReference": "boolean",
    "landlordContact": {
      "name": "string",
      "address": "string",
      "tel": "string (phone format)",
      "email": "string (email format)"
    }
  },
  "other": {
    "pets": {
      "hasPets": "boolean",
      "details": "string"
    },
    "smoke": "boolean",
    "coliving": {
      "hasColiving": "boolean",
      "details": "string"
    }
  },
  "occupationAgreement": {
    "singleOccupancyAgree": "boolean",
    "hmoTermsAgree": "boolean",
    "noUnlistedOccupants": "boolean",
    "noSmoking": "boolean",
    "kitchenCookingOnly": "boolean"
  },
  "consentAndDeclaration": {
    "consentGiven": "boolean",
    "signature": "string",
    "date": "string (YYYY-MM-DD)",
    "printName": "string",
    "declaration": {
      "mainHome": "boolean",
      "enquiriesPermission": "boolean",
      "certifyNoJudgements": "boolean",
      "certifyNoHousingDebt": "boolean",
      "certifyNoLandlordDebt": "boolean",
      "certifyNoAbuse": "boolean"
    },
    "declarationSignature": "string",
    "declarationDate": "string (YYYY-MM-DD)",
    "declarationPrintName": "string"
  }
}
```

## Status Codes

- `Draft` - Form session initialized
- `EmailSent` - Email verification sent
- `EmailVerified` - Email verified successfully
- `Submitted` - Form data submitted
- `PdfGenerated` - PDF generated from form data
- `Completed` - Processing completed successfully
- `Failed` - Processing failed

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Configuration Requirements

Before using the API, ensure the following are configured:

1. **SMTP Settings** - For sending emails
2. **Azure Blob Storage** - For PDF storage
3. **Database Connection** - For submission tracking

See the main README.md for detailed configuration instructions.