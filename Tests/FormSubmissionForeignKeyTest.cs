using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.InMemory;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using BlazorApp.Data;
using BlazorApp.Models;
using BlazorApp.Services;

namespace Tests;

/// <summary>
/// Test to validate that the FormService properly handles foreign key constraints
/// and that the fix for the FOREIGN KEY constraint failure is working correctly.
/// </summary>
public class FormSubmissionForeignKeyTest
{
    public static async Task<bool> TestFormSubmissionForeignKeyConstraints()
    {
        try
        {
            Console.WriteLine("🔍 Testing FormService foreign key constraint handling...");
            
            // Create in-memory database for testing
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
                .Options;

            using var context = new ApplicationDbContext(options);
            
            // Mock dependencies
            var mockEmailService = new Mock<IEmailService>();
            mockEmailService.Setup(x => x.SendEmailVerificationTokenAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(true); // Mock successful email sending
            
            var mockPdfService = new Mock<IPdfGenerationService>();
            var mockBlobService = new Mock<IBlobStorageService>();
            var mockLogger = new Mock<ILogger<FormService>>();
            var mockDebugConsole = new Mock<IDebugConsoleHelper>();
            
            var appSettings = new ApplicationSettings
            {
                TokenExpirationMinutes = 30,
                TokenLength = 6
            };
            var mockAppSettings = new Mock<IOptions<ApplicationSettings>>();
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

            // Test 1: Initialize form session (this was causing the foreign key constraint failure)
            Console.WriteLine("📝 Test 1: Initialize form session");
            var email = "test@example.com";
            var initResult = await formService.InitializeFormSessionAsync(email);
            
            if (!initResult.Success)
            {
                Console.WriteLine($"❌ Form initialization failed: {initResult.Message}");
                return false;
            }
            
            Console.WriteLine($"✅ Form session initialized successfully with ID: {initResult.SubmissionId}");

            // Test 2: Verify the submission was created with proper ID
            var submission = await context.FormSubmissions
                .Include(s => s.Logs)
                .FirstOrDefaultAsync(s => s.SubmissionId == initResult.SubmissionId);
            
            if (submission == null)
            {
                Console.WriteLine("❌ Submission not found in database");
                return false;
            }
            
            if (submission.Id <= 0)
            {
                Console.WriteLine($"❌ Submission has invalid ID: {submission.Id}");
                return false;
            }
            
            Console.WriteLine($"✅ Submission created with valid ID: {submission.Id}");

            // Test 3: Verify the log was created with proper foreign key reference
            if (submission.Logs.Count == 0)
            {
                Console.WriteLine("❌ No logs found for submission");
                return false;
            }
            
            var log = submission.Logs.First();
            if (log.FormSubmissionId != submission.Id)
            {
                Console.WriteLine($"❌ Log foreign key mismatch. Expected: {submission.Id}, Actual: {log.FormSubmissionId}");
                return false;
            }
            
            if (log.Action != "SessionInitialized")
            {
                Console.WriteLine($"❌ Unexpected log action. Expected: SessionInitialized, Actual: {log.Action}");
                return false;
            }
            
            Console.WriteLine($"✅ Log created with correct foreign key reference and action: {log.Action}");

            // Test 4: Test email verification (another operation that uses LogSubmissionAction)
            Console.WriteLine("📝 Test 4: Test email verification");
            var verificationResult = await formService.SendEmailVerificationAsync(initResult.SubmissionId, email);
            
            if (!verificationResult.Success)
            {
                Console.WriteLine($"❌ Email verification failed: {verificationResult.Message}");
                return false;
            }
            
            Console.WriteLine("✅ Email verification request processed successfully");

            // Test 5: Verify additional logs were created correctly
            await context.Entry(submission).ReloadAsync();
            await context.Entry(submission).Collection(s => s.Logs).LoadAsync();
            
            if (submission.Logs.Count < 2)
            {
                Console.WriteLine($"❌ Expected at least 2 logs, found: {submission.Logs.Count}");
                return false;
            }
            
            var emailLog = submission.Logs.FirstOrDefault(l => l.Action == "EmailVerificationSent");
            if (emailLog == null)
            {
                Console.WriteLine("❌ EmailVerificationSent log not found");
                return false;
            }
            
            if (emailLog.FormSubmissionId != submission.Id)
            {
                Console.WriteLine($"❌ Email log foreign key mismatch. Expected: {submission.Id}, Actual: {emailLog.FormSubmissionId}");
                return false;
            }
            
            Console.WriteLine("✅ All logs created with correct foreign key references");

            Console.WriteLine("🎉 All foreign key constraint tests passed!");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Test failed with exception: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            return false;
        }
    }
}