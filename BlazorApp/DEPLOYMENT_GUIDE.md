# Deployment and Configuration Guide

## Quick Start

### Prerequisites
- .NET 8 SDK
- SQL Server (Production) or SQLite (Development)
- Azure Storage Account (for PDF storage)
- SMTP server access (Gmail, SendGrid, etc.)

### Development Setup

1. **Clone and Build**
   ```bash
   cd BlazorApp
   dotnet restore
   dotnet build
   ```

2. **Configure Development Settings**
   The application uses SQLite by default in development. Update `appsettings.Development.json`:
   ```json
   {
     "ConnectionStrings": {
       "DefaultConnection": "Data Source=accommodationform_dev.db"
     },
     "EmailSettings": {
       "SmtpServer": "localhost",
       "SmtpPort": 1025,
       "UseSsl": false,
       "FromEmail": "test@localhost",
       "CompanyEmail": "company@localhost"
     },
     "BlobStorageSettings": {
       "ConnectionString": "UseDevelopmentStorage=true",
       "ContainerName": "form-submissions-dev"
     }
   }
   ```

3. **Run the Application**
   ```bash
   dotnet run
   ```
   - Application: http://localhost:5260
   - Swagger API: http://localhost:5260/swagger
   - Form: http://localhost:5260/application

### Production Deployment

1. **Update Production Configuration**
   Update `appsettings.json` with production values:
   ```json
   {
     "ConnectionStrings": {
       "DefaultConnection": "Server=your-server;Database=AzureAccommodationFormDb;..."
     },
     "EmailSettings": {
       "SmtpServer": "smtp.gmail.com",
       "SmtpPort": 587,
       "SmtpUsername": "your-email@domain.com",
       "SmtpPassword": "your-app-password",
       "FromEmail": "noreply@yourdomain.com",
       "CompanyEmail": "applications@yourdomain.com"
     },
     "BlobStorageSettings": {
       "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=...",
       "ContainerName": "form-submissions"
     }
   }
   ```

2. **Build for Production**
   ```bash
   dotnet publish -c Release -o ./publish
   ```

3. **Deploy to Azure App Service**
   - Create an Azure App Service with .NET 8 runtime
   - Configure connection strings and app settings
   - Deploy the published files

## Configuration Details

### Email Settings
- **SmtpServer**: SMTP server hostname
- **SmtpPort**: SMTP port (typically 587 for TLS)
- **SmtpUsername/Password**: SMTP credentials
- **FromEmail**: Sender email address
- **CompanyEmail**: Email to receive form submissions

### Azure Blob Storage
- **ConnectionString**: Azure Storage connection string
- **ContainerName**: Blob container for PDF storage

### Application Settings
- **TokenExpirationMinutes**: Email verification token validity (default: 15)
- **TokenLength**: Verification token length (default: 6)

## Database Management

### Development (SQLite)
```bash
# View database schema
sqlite3 accommodationform_dev.db ".schema"

# Query submissions
sqlite3 accommodationform_dev.db "SELECT * FROM FormSubmissions;"
```

### Production (SQL Server)
```sql
-- Create database
CREATE DATABASE AzureAccommodationFormDb;

-- View submissions
SELECT * FROM FormSubmissions ORDER BY SubmittedAt DESC;

-- View logs for a submission
SELECT * FROM FormSubmissionLogs WHERE FormSubmissionId = 1;
```

## Monitoring and Logging

The application includes comprehensive logging:
- Form submission workflow tracking
- Email sending status
- PDF generation results
- Blob storage operations
- API request/response logging

### View Application Logs
```bash
# In development
dotnet run --verbosity normal

# In production (Azure App Service)
# Check Application Insights or App Service logs
```

## Security Considerations

### Current Implementation
- HTTPS enforcement
- Email verification workflow
- Input validation and sanitization
- SQL injection protection (EF Core)

### Production Recommendations
1. **Enable HTTPS Only**
2. **Configure CORS appropriately**
3. **Implement rate limiting**
4. **Add authentication for admin endpoints**
5. **Enable Application Insights**

## API Usage

### Form Submission Workflow

1. **Initialize Form Session**
   ```bash
   curl -X POST "https://your-domain.com/api/form/initialize" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com"}'
   ```

2. **Send Email Verification**
   ```bash
   curl -X POST "https://your-domain.com/api/form/send-verification" \
     -H "Content-Type: application/json" \
     -d '{"submissionId": "your-id", "email": "user@example.com"}'
   ```

3. **Verify Email Token**
   ```bash
   curl -X POST "https://your-domain.com/api/form/verify-email" \
     -H "Content-Type: application/json" \
     -d '{"submissionId": "your-id", "token": "123456"}'
   ```

4. **Submit Form Data**
   ```bash
   curl -X POST "https://your-domain.com/api/form/submit" \
     -H "Content-Type: application/json" \
     -d '{"submissionId": "your-id", "formData": {...}}'
   ```

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check SMTP settings
   - Verify firewall rules
   - Test SMTP connectivity

2. **Database connection issues**
   - Verify connection string
   - Check SQL Server availability
   - Review network connectivity

3. **Blob storage errors**
   - Validate Azure Storage credentials
   - Check container permissions
   - Monitor storage account health

4. **PDF generation fails**
   - Check available memory
   - Review file system permissions
   - Monitor CPU usage

### Debug Mode
Enable detailed logging in `appsettings.Development.json`:
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.EntityFrameworkCore": "Information"
    }
  }
}
```

## Maintenance Tasks

### Regular Maintenance
1. **Monitor database size and performance**
2. **Archive old form submissions**
3. **Clean up blob storage**
4. **Review error logs**
5. **Update dependencies**

### Backup Strategy
1. **Database backups** (automated in Azure SQL)
2. **Blob storage redundancy** (built-in Azure feature)
3. **Application configuration backup**

## Performance Optimization

### Recommendations
1. **Enable response compression**
2. **Implement caching for static content**
3. **Optimize database queries**
4. **Use CDN for static assets**
5. **Monitor Application Insights metrics**

## Support and Documentation

- **API Documentation**: Available at `/swagger` endpoint
- **Application Logs**: Available in Azure App Service logs
- **Health Checks**: Can be added to monitor service health
- **Error Tracking**: Integrated with Application Insights (when configured)