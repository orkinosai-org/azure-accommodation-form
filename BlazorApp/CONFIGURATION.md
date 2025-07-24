# Configuration Guide for appsettings.json

This document explains how to configure the `appsettings.json` file for the Azure Accommodation Form application.

## Configuration Sections

### ConnectionStrings
Replace `<your_database_connection_string>` with your database connection string:
- **SQLite (Development)**: `Data Source=accommodationform.db`
- **SQL Server (Production)**: `Server=your-server;Database=your-database;User Id=your-username;Password=your-password;TrustServerCertificate=true;`

### EmailSettings
Configure your SMTP server for sending email notifications:

- **SmtpServer**: Replace `<your_smtp_server>` with your SMTP server hostname
  - Examples: `smtp.gmail.com`, `smtp.sendgrid.net`, `smtp.office365.com`
- **SmtpPort**: SMTP port number (587 is recommended for TLS)
- **SmtpUsername**: Replace `<your_smtp_username>` with your SMTP username/email
- **SmtpPassword**: Replace `<your_smtp_password>` with your SMTP password or app-specific password
- **UseSsl**: Keep as `true` for secure connections
- **FromEmail**: Replace `<your_from_email>` with the email address that will appear as the sender
- **FromName**: Replace `<your_from_name>` with the display name for the sender
- **CompanyEmail**: Replace `<your_company_email>` with the email address to receive form submissions

### BlobStorageSettings
Configure Azure Blob Storage for file storage:

- **ConnectionString**: Replace `<your_azure_blob_connection_string>` with your Azure Storage connection string
  - Format: `DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=yourkey;EndpointSuffix=core.windows.net`
  - For development: Use `UseDevelopmentStorage=true` with Azure Storage Emulator
- **ContainerName**: Replace `<your_container_name>` with your blob container name (e.g., `form-submissions`)

### ApplicationSettings
Configure application-specific settings:

- **ApplicationName**: Replace `<your_application_name>` with your application's display name
- **ApplicationUrl**: Replace `<your_application_url>` with your application's public URL
  - Examples: `https://yourdomain.com`, `https://yourapp.azurewebsites.net`
- **TokenExpirationMinutes**: Email verification token validity in minutes (default: 15)
- **TokenLength**: Email verification token character length (default: 6)

## Example Configurations

### Development Configuration
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=accommodationform_dev.db"
  },
  "EmailSettings": {
    "SmtpServer": "localhost",
    "SmtpPort": 1025,
    "SmtpUsername": "",
    "SmtpPassword": "",
    "UseSsl": false,
    "FromEmail": "noreply@localhost",
    "FromName": "Development App",
    "CompanyEmail": "test@localhost"
  },
  "BlobStorageSettings": {
    "ConnectionString": "UseDevelopmentStorage=true",
    "ContainerName": "form-submissions-dev"
  },
  "ApplicationSettings": {
    "ApplicationName": "My App (Development)",
    "ApplicationUrl": "https://localhost:5001"
  }
}
```

### Production Configuration Example
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=myserver.database.windows.net;Database=AccommodationFormDb;User Id=myuser;Password=mypassword;TrustServerCertificate=true;"
  },
  "EmailSettings": {
    "SmtpServer": "smtp.sendgrid.net",
    "SmtpPort": 587,
    "SmtpUsername": "apikey",
    "SmtpPassword": "your_sendgrid_api_key",
    "UseSsl": true,
    "FromEmail": "noreply@yourdomain.com",
    "FromName": "Your Company Name",
    "CompanyEmail": "forms@yourdomain.com"
  },
  "BlobStorageSettings": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=mykey;EndpointSuffix=core.windows.net",
    "ContainerName": "form-submissions"
  },
  "ApplicationSettings": {
    "ApplicationName": "Your Application Name",
    "ApplicationUrl": "https://yourdomain.com"
  }
}
```

## Security Notes

- **Never commit real secrets to version control**
- Use environment variables or Azure Key Vault for production secrets
- The provided `appsettings.json` template contains placeholder values that are safe for any client
- Always use strong, unique passwords for SMTP and database connections
- Enable SSL/TLS for SMTP connections in production