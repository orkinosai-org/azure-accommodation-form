using System;
using System.Reflection;
using Microsoft.Extensions.Logging;
using Moq;
using BlazorApp.Data;
using BlazorApp.Services;
using Microsoft.EntityFrameworkCore;

namespace Tests;

/// <summary>
/// Quick test to verify that the defensive LogSubmissionAction method handles invalid submission IDs gracefully
/// </summary>
public class DefensiveLoggingTest
{
    public static async Task<bool> TestDefensiveLogging()
    {
        try
        {
            Console.WriteLine("🔍 Testing defensive logging in FormService...");
            
            // Create in-memory database for testing
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
                .Options;

            using var context = new ApplicationDbContext(options);
            
            // Mock dependencies
            var mockEmailService = new Mock<IEmailService>();
            var mockPdfService = new Mock<IPdfGenerationService>();
            var mockBlobService = new Mock<IBlobStorageService>();
            var mockLogger = new Mock<ILogger<FormService>>();
            var mockDebugConsole = new Mock<IDebugConsoleHelper>();
            
            var appSettings = new ApplicationSettings();
            var mockAppSettings = new Mock<Microsoft.Extensions.Options.IOptions<ApplicationSettings>>();
            mockAppSettings.Setup(x => x.Value).Returns(appSettings);

            // Create FormService instance
            var formService = new FormService(
                context,
                mockEmailService.Object,
                mockPdfService.Object,
                mockBlobService.Object,
                mockAppSettings.Object,
                mockLogger.Object,
                mockDebugConsole.Object
            );

            // Use reflection to access the private LogSubmissionAction method
            var logMethod = typeof(FormService).GetMethod("LogSubmissionAction", BindingFlags.NonPublic | BindingFlags.Instance);
            if (logMethod == null)
            {
                Console.WriteLine("❌ Could not find LogSubmissionAction method");
                return false;
            }

            // Test defensive check with invalid submission ID
            Console.WriteLine("📝 Testing LogSubmissionAction with invalid submission ID (0)");
            logMethod.Invoke(formService, new object[] { 0, "TestAction", "Test details" });
            
            Console.WriteLine("📝 Testing LogSubmissionAction with negative submission ID (-1)");
            logMethod.Invoke(formService, new object[] { -1, "TestAction", "Test details" });
            
            // Verify that no logs were added to the context
            var logCount = await context.FormSubmissionLogs.CountAsync();
            if (logCount != 0)
            {
                Console.WriteLine($"❌ Expected 0 logs, but found {logCount}");
                return false;
            }
            
            Console.WriteLine("✅ Defensive logging correctly prevented invalid foreign key references");
            
            // Verify that the logger was called for error logging
            mockLogger.Verify(
                x => x.Log(
                    LogLevel.Error,
                    It.IsAny<EventId>(),
                    It.Is<It.IsAnyType>((v, t) => v.ToString().Contains("Cannot log submission action")),
                    It.IsAny<Exception>(),
                    It.IsAny<Func<It.IsAnyType, Exception, string>>()),
                Times.AtLeast(2));
            
            Console.WriteLine("✅ Error logging verification passed");
            Console.WriteLine("🎉 All defensive logging tests passed!");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Defensive logging test failed: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            return false;
        }
    }
}