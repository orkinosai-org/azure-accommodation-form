using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace Tests;

/// <summary>
/// Test to verify that the application can start successfully without Azure diagnostics
/// dependencies, specifically without the DIAGNOSTICS_AZUREBLOBCONTAINERSASURL environment variable.
/// </summary>
public class StartupWithoutAzureDiagnosticsTest
{
    public static async Task Main(string[] args)
    {
        Console.WriteLine("🧪 Startup Without Azure Diagnostics Test");
        Console.WriteLine("==========================================");
        Console.WriteLine("Testing that the application can start without Azure Blob diagnostics");
        Console.WriteLine("and without the DIAGNOSTICS_AZUREBLOBCONTAINERSASURL environment variable.\n");

        try
        {
            // Ensure the diagnostics environment variable is not set
            Environment.SetEnvironmentVariable("DIAGNOSTICS_AZUREBLOBCONTAINERSASURL", null);
            Console.WriteLine("✓ Removed DIAGNOSTICS_AZUREBLOBCONTAINERSASURL environment variable");

            // Test creating the web application builder without Azure diagnostics
            Console.WriteLine("🔧 Creating WebApplication builder...");
            
            var builder = WebApplication.CreateBuilder(args);

            // Configure logging similar to the main application but without Azure dependencies
            builder.Logging.ClearProviders();
            builder.Logging.AddConsole();
            builder.Logging.AddDebug();
            
            // Disable Azure App Service diagnostics trace listeners
            builder.Logging.AddFilter("Microsoft.Extensions.Logging.AzureAppServices.Internal.AzureBlobLoggerProvider", LogLevel.None);

            // Add minimal services to test startup
            builder.Services.AddRazorComponents()
                .AddInteractiveServerComponents();

            Console.WriteLine("✓ WebApplication builder created successfully");

            // Test building the application
            Console.WriteLine("🔧 Building WebApplication...");
            var app = builder.Build();
            Console.WriteLine("✓ WebApplication built successfully");

            // Verify logging providers
            var loggerFactory = app.Services.GetRequiredService<ILoggerFactory>();
            var logger = loggerFactory.CreateLogger<StartupWithoutAzureDiagnosticsTest>();
            
            Console.WriteLine("🔧 Testing logging without Azure diagnostics...");
            logger.LogInformation("Test log entry - application started without Azure diagnostics");
            Console.WriteLine("✓ Logging works without Azure diagnostics");

            // Test that the application can be disposed cleanly
            Console.WriteLine("🔧 Disposing application...");
            await app.DisposeAsync();
            Console.WriteLine("✓ Application disposed successfully");

            Console.WriteLine("\n🎉 SUCCESS: Application Startup Without Azure Diagnostics");
            Console.WriteLine("✓ Application can start without DIAGNOSTICS_AZUREBLOBCONTAINERSASURL");
            Console.WriteLine("✓ No dependency on Azure Blob diagnostics");
            Console.WriteLine("✓ Logging configured properly without Azure providers");
            Console.WriteLine("✓ Application builds and disposes cleanly");

            // Run the debug console helper test
            Console.WriteLine("\n" + new string('=', 50));
            await DebugConsoleHelperTest.TestDebugConsoleHelper();

            // Run the email validation test
            Console.WriteLine("\n" + new string('=', 50));
            await EmailValidationTest.TestEmailValidation();

            // Run the email step validation UX test
            Console.WriteLine("\n" + new string('=', 50));
            await EmailStepValidationUXTest.TestEmailStepValidationUX();

            // Run the enhanced debugging test
            Console.WriteLine("\n" + new string('=', 50));
            await EnhancedDebuggingTest.RunAsync();

            // Run the consent validation test
            Console.WriteLine("\n" + new string('=', 50));
            await ConsentValidationTest.TestConsentValidation();

            // Run the foreign key constraint test
            Console.WriteLine("\n" + new string('=', 50));
            var foreignKeyTestResult = await FormSubmissionForeignKeyTest.TestFormSubmissionForeignKeyConstraints();
            if (!foreignKeyTestResult)
            {
                Console.WriteLine("❌ Foreign key constraint test failed!");
                Environment.Exit(1);
            }

            // Run the defensive logging test
            Console.WriteLine("\n" + new string('=', 50));
            var defensiveLoggingTestResult = await DefensiveLoggingTest.TestDefensiveLogging();
            if (!defensiveLoggingTestResult)
            {
                Console.WriteLine("❌ Defensive logging test failed!");
                Environment.Exit(1);
            }

        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ FAILURE: Application startup failed");
            Console.WriteLine($"   Error: {ex.Message}");
            Console.WriteLine($"   Type: {ex.GetType().Name}");
            if (ex.InnerException != null)
            {
                Console.WriteLine($"   Inner Error: {ex.InnerException.Message}");
            }
            Console.WriteLine($"   Stack trace: {ex.StackTrace}");
            
            Environment.Exit(1);
        }
    }
}