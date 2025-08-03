using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using BlazorApp.Data;
using BlazorApp.Models;
using BlazorApp.Services;

namespace Tests;

/// <summary>
/// Integration test to verify that the FormService foreign key fix works in a realistic scenario
/// that simulates the actual application flow without external dependencies.
/// </summary>
public class FormSubmissionIntegrationTest
{
    public static async Task<bool> TestFormSubmissionIntegration()
    {
        try
        {
            Console.WriteLine("🔄 Running FormService integration test...");
            Console.WriteLine("Testing the complete form submission flow with fixed foreign key constraints");
            
            // Create InMemory database to simulate real database behavior with proper schema
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
                .Options;

            using var context = new ApplicationDbContext(options);
            
            // InMemory database doesn't need explicit schema creation
            Console.WriteLine("✓ Test database ready");
            
            // Setup service dependencies with mock implementations
            var mockEmailService = new Mock<IEmailService>();
            mockEmailService.Setup(x => x.SendEmailVerificationTokenAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(true);
            
            var mockPdfService = new Mock<IPdfGenerationService>();
            var mockBlobService = new Mock<IBlobStorageService>();
            
            // Setup logging
            var loggerFactory = LoggerFactory.Create(builder => builder.AddConsole());
            var logger = loggerFactory.CreateLogger<FormService>();
            
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
                logger,
                mockDebugConsole.Object
            );

            Console.WriteLine("✓ FormService created with dependencies");

            // Test 1: Initialize multiple form sessions (this was the problematic area)
            Console.WriteLine("\n📝 Test 1: Initialize multiple form sessions");
            
            var email1 = "user1@example.com";
            var email2 = "user2@example.com";
            
            var result1 = await formService.InitializeFormSessionAsync(email1);
            var result2 = await formService.InitializeFormSessionAsync(email2);
            
            if (!result1.Success || !result2.Success)
            {
                Console.WriteLine($"❌ Session initialization failed. Result1: {result1.Success}, Result2: {result2.Success}");
                Console.WriteLine($"   Error messages: {result1.Message}, {result2.Message}");
                return false;
            }
            
            Console.WriteLine($"✅ Sessions initialized: {result1.SubmissionId}, {result2.SubmissionId}");

            // Test 2: Verify database state - check submissions and logs
            Console.WriteLine("\n📝 Test 2: Verify database integrity");
            
            var submissions = await context.FormSubmissions
                .Include(s => s.Logs)
                .ToListAsync();
            
            if (submissions.Count != 2)
            {
                Console.WriteLine($"❌ Expected 2 submissions, found {submissions.Count}");
                return false;
            }
            
            foreach (var submission in submissions)
            {
                if (submission.Id <= 0)
                {
                    Console.WriteLine($"❌ Submission has invalid ID: {submission.Id}");
                    return false;
                }
                
                if (submission.Logs.Count == 0)
                {
                    Console.WriteLine($"❌ No logs found for submission {submission.Id}");
                    return false;
                }
                
                var log = submission.Logs.First();
                if (log.FormSubmissionId != submission.Id)
                {
                    Console.WriteLine($"❌ Foreign key mismatch. Submission ID: {submission.Id}, Log FK: {log.FormSubmissionId}");
                    return false;
                }
                
                if (log.Action != "SessionInitialized")
                {
                    Console.WriteLine($"❌ Unexpected log action: {log.Action}");
                    return false;
                }
            }
            
            Console.WriteLine("✅ Database integrity verified - all foreign keys correct");

            // Test 3: Email verification flow
            Console.WriteLine("\n📝 Test 3: Email verification flow");
            
            var emailResult1 = await formService.SendEmailVerificationAsync(result1.SubmissionId, email1);
            var emailResult2 = await formService.SendEmailVerificationAsync(result2.SubmissionId, email2);
            
            if (!emailResult1.Success || !emailResult2.Success)
            {
                Console.WriteLine($"❌ Email verification failed. Result1: {emailResult1.Success}, Result2: {emailResult2.Success}");
                return false;
            }
            
            Console.WriteLine("✅ Email verification requests processed successfully");

            // Test 4: Verify additional logs were created correctly
            Console.WriteLine("\n📝 Test 4: Verify additional logging");
            
            await context.Entry(submissions[0]).Collection(s => s.Logs).LoadAsync();
            await context.Entry(submissions[1]).Collection(s => s.Logs).LoadAsync();
            
            foreach (var submission in submissions)
            {
                if (submission.Logs.Count < 2)
                {
                    Console.WriteLine($"❌ Expected at least 2 logs for submission {submission.Id}, found {submission.Logs.Count}");
                    return false;
                }
                
                var hasEmailLog = submission.Logs.Any(l => l.Action == "EmailVerificationSent");
                if (!hasEmailLog)
                {
                    Console.WriteLine($"❌ EmailVerificationSent log not found for submission {submission.Id}");
                    return false;
                }
                
                // Verify all logs have correct foreign keys
                foreach (var log in submission.Logs)
                {
                    if (log.FormSubmissionId != submission.Id)
                    {
                        Console.WriteLine($"❌ Log foreign key mismatch. Expected: {submission.Id}, Actual: {log.FormSubmissionId}");
                        return false;
                    }
                }
            }
            
            Console.WriteLine("✅ All logs created with correct foreign key references");

            // Test 5: Concurrent operations test
            Console.WriteLine("\n📝 Test 5: Concurrent operations test");
            
            var concurrentTasks = new List<Task<FormSubmissionResponse>>();
            for (int i = 0; i < 5; i++)
            {
                var email = $"concurrent{i}@example.com";
                concurrentTasks.Add(formService.InitializeFormSessionAsync(email));
            }
            
            var concurrentResults = await Task.WhenAll(concurrentTasks);
            
            if (concurrentResults.Any(r => !r.Success))
            {
                Console.WriteLine("❌ Some concurrent operations failed");
                return false;
            }
            
            Console.WriteLine("✅ Concurrent operations completed successfully");

            // Final verification
            var finalSubmissionCount = await context.FormSubmissions.CountAsync();
            var finalLogCount = await context.FormSubmissionLogs.CountAsync();
            
            Console.WriteLine($"\n📊 Final database state:");
            Console.WriteLine($"   Submissions: {finalSubmissionCount}");
            Console.WriteLine($"   Logs: {finalLogCount}");
            
            if (finalSubmissionCount != 7 || finalLogCount < 7) // 2 initial + 5 concurrent = 7 submissions, at least 7 logs
            {
                Console.WriteLine($"❌ Unexpected database state. Expected 7 submissions and at least 7 logs");
                return false;
            }
            
            Console.WriteLine("🎉 All integration tests passed!");
            Console.WriteLine("✅ Foreign key constraint fix is working correctly in realistic scenarios");
            Console.WriteLine("✅ Form submission initialization works reliably");
            Console.WriteLine("✅ Database integrity maintained under concurrent operations");
            
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Integration test failed with exception: {ex.Message}");
            Console.WriteLine($"   Exception type: {ex.GetType().Name}");
            Console.WriteLine($"   Stack trace: {ex.StackTrace}");
            return false;
        }
    }
}