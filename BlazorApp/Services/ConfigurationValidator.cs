using Microsoft.Extensions.Options;

namespace BlazorApp.Services;

public interface IConfigurationValidator
{
    Task ValidateConfigurationAsync();
}

public class ConfigurationValidator : IConfigurationValidator
{
    private readonly EmailSettings _emailSettings;
    private readonly BlobStorageSettings _blobSettings;
    private readonly ApplicationSettings _appSettings;
    private readonly ILogger<ConfigurationValidator> _logger;
    private readonly IConfiguration _configuration;

    public ConfigurationValidator(
        IOptions<EmailSettings> emailSettings,
        IOptions<BlobStorageSettings> blobSettings,
        IOptions<ApplicationSettings> appSettings,
        ILogger<ConfigurationValidator> logger,
        IConfiguration configuration)
    {
        _emailSettings = emailSettings.Value;
        _blobSettings = blobSettings.Value;
        _appSettings = appSettings.Value;
        _logger = logger;
        _configuration = configuration;
    }

    public async Task ValidateConfigurationAsync()
    {
        _logger.LogInformation("=== CONFIGURATION VALIDATION STARTED ===");
        
        await ValidateEmailConfigurationAsync();
        await ValidateBlobStorageConfigurationAsync();
        await ValidateApplicationConfigurationAsync();
        
        _logger.LogInformation("=== CONFIGURATION VALIDATION COMPLETED ===");
    }

    private async Task ValidateEmailConfigurationAsync()
    {
        var configSource = GetConfigurationSource("EmailSettings");
        _logger.LogInformation("Email configuration loaded from: {ConfigSource}", configSource);

        var issues = new List<string>();

        // Validate required SMTP settings
        if (string.IsNullOrWhiteSpace(_emailSettings.SmtpServer))
        {
            issues.Add("SmtpServer is not configured");
        }

        if (_emailSettings.SmtpPort <= 0 || _emailSettings.SmtpPort > 65535)
        {
            issues.Add($"SmtpPort is invalid: {_emailSettings.SmtpPort} (must be between 1-65535)");
        }

        if (string.IsNullOrWhiteSpace(_emailSettings.SmtpUsername))
        {
            issues.Add("SmtpUsername is not configured - email sending may fail");
        }

        if (string.IsNullOrWhiteSpace(_emailSettings.SmtpPassword))
        {
            issues.Add("SmtpPassword is not configured - email sending may fail");
        }

        if (string.IsNullOrWhiteSpace(_emailSettings.FromEmail))
        {
            issues.Add("FromEmail is not configured");
        }

        if (string.IsNullOrWhiteSpace(_emailSettings.FromName))
        {
            issues.Add("FromName is not configured");
        }

        if (string.IsNullOrWhiteSpace(_emailSettings.CompanyEmail))
        {
            issues.Add("CompanyEmail is not configured");
        }

        // Log current configuration (masking sensitive data)
        _logger.LogInformation("SMTP Configuration Status:");
        _logger.LogInformation("  SmtpServer: {SmtpServer}", _emailSettings.SmtpServer);
        _logger.LogInformation("  SmtpPort: {SmtpPort}", _emailSettings.SmtpPort);
        _logger.LogInformation("  UseSsl: {UseSsl}", _emailSettings.UseSsl);
        _logger.LogInformation("  SmtpUsername: {Username}", MaskSensitiveData(_emailSettings.SmtpUsername));
        _logger.LogInformation("  SmtpPassword: {Password}", MaskPassword(_emailSettings.SmtpPassword));
        _logger.LogInformation("  FromEmail: {FromEmail}", _emailSettings.FromEmail);
        _logger.LogInformation("  FromName: {FromName}", _emailSettings.FromName);
        _logger.LogInformation("  CompanyEmail: {CompanyEmail}", _emailSettings.CompanyEmail);

        if (issues.Any())
        {
            foreach (var issue in issues)
            {
                _logger.LogWarning("SMTP Configuration Issue: {Issue}", issue);
            }

            _logger.LogWarning("Email functionality may not work properly. To fix these issues:");
            _logger.LogWarning("1. Set environment variables:");
            _logger.LogWarning("   - EmailSettings__SmtpServer=smtp.gmail.com");
            _logger.LogWarning("   - EmailSettings__SmtpUsername=your-email@gmail.com");
            _logger.LogWarning("   - EmailSettings__SmtpPassword=your-app-password");
            _logger.LogWarning("   - EmailSettings__FromEmail=noreply@yourdomain.com");
            _logger.LogWarning("   - EmailSettings__CompanyEmail=admin@yourdomain.com");
            _logger.LogWarning("2. Or update appsettings.json with proper values");
            _logger.LogWarning("3. For Gmail, use App Passwords instead of regular passwords");
        }
        else
        {
            _logger.LogInformation("✓ Email configuration is complete and valid");
        }

        await Task.CompletedTask;
    }

    private async Task ValidateBlobStorageConfigurationAsync()
    {
        var configSource = GetConfigurationSource("BlobStorageSettings");
        _logger.LogInformation("Blob Storage configuration loaded from: {ConfigSource}", configSource);

        var issues = new List<string>();

        if (string.IsNullOrWhiteSpace(_blobSettings.ConnectionString))
        {
            issues.Add("ConnectionString is not configured");
        }

        if (string.IsNullOrWhiteSpace(_blobSettings.ContainerName))
        {
            issues.Add("ContainerName is not configured");
        }

        _logger.LogInformation("Blob Storage Configuration Status:");
        _logger.LogInformation("  ConnectionString: {ConnectionString}", MaskSensitiveData(_blobSettings.ConnectionString));
        _logger.LogInformation("  ContainerName: {ContainerName}", _blobSettings.ContainerName);

        if (issues.Any())
        {
            foreach (var issue in issues)
            {
                _logger.LogWarning("Blob Storage Configuration Issue: {Issue}", issue);
            }

            _logger.LogWarning("File storage functionality may not work properly. To fix:");
            _logger.LogWarning("1. Set environment variables:");
            _logger.LogWarning("   - BlobStorageSettings__ConnectionString=DefaultEndpointsProtocol=https;AccountName=...");
            _logger.LogWarning("   - BlobStorageSettings__ContainerName=form-submissions");
            _logger.LogWarning("2. Or update appsettings.json with proper Azure Storage values");
        }
        else
        {
            _logger.LogInformation("✓ Blob Storage configuration is complete and valid");
        }

        await Task.CompletedTask;
    }

    private async Task ValidateApplicationConfigurationAsync()
    {
        var configSource = GetConfigurationSource("ApplicationSettings");
        _logger.LogInformation("Application configuration loaded from: {ConfigSource}", configSource);

        _logger.LogInformation("Application Configuration:");
        _logger.LogInformation("  ApplicationName: {ApplicationName}", _appSettings.ApplicationName);
        _logger.LogInformation("  ApplicationUrl: {ApplicationUrl}", _appSettings.ApplicationUrl);
        _logger.LogInformation("  TokenExpirationMinutes: {TokenExpirationMinutes}", _appSettings.TokenExpirationMinutes);
        _logger.LogInformation("  TokenLength: {TokenLength}", _appSettings.TokenLength);

        if (_appSettings.TokenExpirationMinutes <= 0)
        {
            _logger.LogWarning("TokenExpirationMinutes should be greater than 0, current value: {Value}", _appSettings.TokenExpirationMinutes);
        }

        if (_appSettings.TokenLength < 4 || _appSettings.TokenLength > 8)
        {
            _logger.LogWarning("TokenLength should be between 4-8 characters, current value: {Value}", _appSettings.TokenLength);
        }

        await Task.CompletedTask;
    }

    private string GetConfigurationSource(string sectionName)
    {
        var sources = new List<string>();

        // Check environment variables
        var envVarPrefix = sectionName + "__";
        var envVars = Environment.GetEnvironmentVariables()
            .Cast<System.Collections.DictionaryEntry>()
            .Where(x => x.Key.ToString()!.StartsWith(envVarPrefix, StringComparison.OrdinalIgnoreCase))
            .ToList();

        if (envVars.Any())
        {
            sources.Add($"Environment Variables ({envVars.Count} settings)");
        }

        // Check configuration files
        var configSection = _configuration.GetSection(sectionName);
        if (configSection.Exists() && configSection.GetChildren().Any())
        {
            sources.Add("Configuration Files (appsettings.json)");
        }

        return sources.Any() ? string.Join(", ", sources) : "Default Values";
    }

    private static string MaskSensitiveData(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return "***NOT SET***";
        }

        if (value.Length <= 4)
        {
            return "***CONFIGURED***";
        }

        return value.Substring(0, 2) + "***" + value.Substring(value.Length - 2);
    }

    private static string MaskPassword(string password)
    {
        if (string.IsNullOrWhiteSpace(password))
        {
            return "***NOT SET***";
        }

        return "***CONFIGURED***";
    }
}