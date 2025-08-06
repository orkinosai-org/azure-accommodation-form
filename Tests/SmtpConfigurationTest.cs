using BlazorApp.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace Tests;

/// <summary>
/// Test class to verify SMTP configuration validation functionality
/// This test ensures that the ConfigurationValidator and EmailService properly validate SMTP settings
/// </summary>
public class SmtpConfigurationTest
{
    public static async Task TestSmtpConfigurationValidation()
    {
        Console.WriteLine("=== SMTP CONFIGURATION VALIDATION TEST ===");
        Console.WriteLine("Testing SMTP configuration validation functionality...");

        // Test valid configuration
        await TestConfigurationValidation_WithValidConfig_ShouldPass();
        
        // Test missing configuration
        await TestConfigurationValidation_WithMissingSmtpConfig_ShouldLogWarnings();
        
        // Test EmailService validation
        TestEmailService_ValidateSmtpConfiguration_WithEmptyConfig_ShouldReturnFalse();
        TestEmailService_ValidateSmtpConfiguration_WithValidConfig_ShouldReturnTrue();
        
        Console.WriteLine("✓ All SMTP configuration validation tests passed!");
    }

    private static async Task TestConfigurationValidation_WithValidConfig_ShouldPass()
    {
        Console.WriteLine("Testing configuration validation with valid config...");

        var inMemorySettings = new Dictionary<string, string>
        {
            {"EmailSettings:SmtpServer", "smtp.gmail.com"},
            {"EmailSettings:SmtpPort", "587"},
            {"EmailSettings:SmtpUsername", "test@gmail.com"},
            {"EmailSettings:SmtpPassword", "testpassword"},
            {"EmailSettings:UseSsl", "true"},
            {"EmailSettings:FromEmail", "noreply@test.com"},
            {"EmailSettings:FromName", "Test Form"},
            {"EmailSettings:CompanyEmail", "admin@test.com"},
            {"BlobStorageSettings:ConnectionString", "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=testkey;EndpointSuffix=core.windows.net"},
            {"BlobStorageSettings:ContainerName", "test-container"},
            {"ApplicationSettings:ApplicationName", "Test App"},
            {"ApplicationSettings:ApplicationUrl", "https://test.com"},
            {"ApplicationSettings:TokenExpirationMinutes", "15"},
            {"ApplicationSettings:TokenLength", "6"}
        };

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(inMemorySettings!)
            .Build();

        var emailSettings = Options.Create(new EmailSettings
        {
            SmtpServer = "smtp.gmail.com",
            SmtpPort = 587,
            SmtpUsername = "test@gmail.com",
            SmtpPassword = "testpassword",
            UseSsl = true,
            FromEmail = "noreply@test.com",
            FromName = "Test Form",
            CompanyEmail = "admin@test.com"
        });

        var blobSettings = Options.Create(new BlobStorageSettings
        {
            ConnectionString = "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=testkey;EndpointSuffix=core.windows.net",
            ContainerName = "test-container"
        });

        var appSettings = Options.Create(new ApplicationSettings
        {
            ApplicationName = "Test App",
            ApplicationUrl = "https://test.com",
            TokenExpirationMinutes = 15,
            TokenLength = 6
        });

        var logger = new LoggerFactory().CreateLogger<ConfigurationValidator>();

        var validator = new ConfigurationValidator(emailSettings, blobSettings, appSettings, logger, configuration);

        // Should not throw
        await validator.ValidateConfigurationAsync();
        Console.WriteLine("✓ Valid configuration passed validation");
    }

    private static async Task TestConfigurationValidation_WithMissingSmtpConfig_ShouldLogWarnings()
    {
        Console.WriteLine("Testing configuration validation with missing SMTP config...");

        var inMemorySettings = new Dictionary<string, string>
        {
            {"EmailSettings:SmtpServer", ""},
            {"EmailSettings:SmtpUsername", ""},
            {"EmailSettings:SmtpPassword", ""},
            {"BlobStorageSettings:ConnectionString", ""},
            {"ApplicationSettings:ApplicationName", "Test App"}
        };

        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(inMemorySettings!)
            .Build();

        var emailSettings = Options.Create(new EmailSettings()); // Empty settings
        var blobSettings = Options.Create(new BlobStorageSettings());
        var appSettings = Options.Create(new ApplicationSettings
        {
            ApplicationName = "Test App",
            TokenExpirationMinutes = 15,
            TokenLength = 6
        });

        var loggerFactory = new LoggerFactory();
        var logger = loggerFactory.CreateLogger<ConfigurationValidator>();

        var validator = new ConfigurationValidator(emailSettings, blobSettings, appSettings, logger, configuration);

        // Should not throw but will log warnings
        await validator.ValidateConfigurationAsync();
        Console.WriteLine("✓ Missing configuration handled correctly with warnings");
    }

    private static void TestEmailService_ValidateSmtpConfiguration_WithEmptyConfig_ShouldReturnFalse()
    {
        Console.WriteLine("Testing EmailService validation with empty config...");

        var emailSettings = Options.Create(new EmailSettings()); // Empty settings
        var appSettings = Options.Create(new ApplicationSettings());
        var logger = new LoggerFactory().CreateLogger<EmailService>();
        var mockDebugConsole = new MockDebugConsoleHelper();

        var emailService = new EmailService(emailSettings, appSettings, logger, mockDebugConsole);

        // Access the private ValidateSmtpConfiguration method via reflection for testing
        var method = typeof(EmailService).GetMethod("ValidateSmtpConfiguration", 
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        var result = (bool)method!.Invoke(emailService, null)!;

        if (!result)
        {
            Console.WriteLine("✓ Empty config correctly returned false");
        }
        else
        {
            throw new Exception("Expected empty config to return false, but got true");
        }
    }

    private static void TestEmailService_ValidateSmtpConfiguration_WithValidConfig_ShouldReturnTrue()
    {
        Console.WriteLine("Testing EmailService validation with valid config...");

        var emailSettings = Options.Create(new EmailSettings
        {
            SmtpServer = "smtp.gmail.com",
            SmtpPort = 587,
            SmtpUsername = "test@gmail.com",
            SmtpPassword = "testpassword",
            FromEmail = "noreply@test.com"
        });
        var appSettings = Options.Create(new ApplicationSettings());
        var logger = new LoggerFactory().CreateLogger<EmailService>();
        var mockDebugConsole = new MockDebugConsoleHelper();

        var emailService = new EmailService(emailSettings, appSettings, logger, mockDebugConsole);

        // Access the private ValidateSmtpConfiguration method via reflection for testing
        var method = typeof(EmailService).GetMethod("ValidateSmtpConfiguration", 
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        var result = (bool)method!.Invoke(emailService, null)!;

        if (result)
        {
            Console.WriteLine("✓ Valid config correctly returned true");
        }
        else
        {
            throw new Exception("Expected valid config to return true, but got false");
        }
    }
}

// Mock implementation for testing
public class MockDebugConsoleHelper : IDebugConsoleHelper
{
    public Task LogAsync(string message, string level = "log") => Task.CompletedTask;
    public Task LogInfoAsync(string message) => Task.CompletedTask;
    public Task LogWarningAsync(string message) => Task.CompletedTask;
    public Task LogErrorAsync(string message) => Task.CompletedTask;
    public Task LogGroupAsync(string groupName) => Task.CompletedTask;
    public Task LogGroupEndAsync() => Task.CompletedTask;
}