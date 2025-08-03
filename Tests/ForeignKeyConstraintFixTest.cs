using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.InMemory;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using BlazorApp.Data;
using BlazorApp.Models;
using BlazorApp.Services;
using System;
using System.Threading.Tasks;

namespace Tests
{
    /// <summary>
    /// Test to reproduce and validate the fix for foreign key constraint failures
    /// in FormService when LogSubmissionAction is called before parent entity is saved
    /// </summary>
    public class ForeignKeyConstraintFixTest
    {
        public static async Task<bool> TestForeignKeyConstraintFix()
        {
            try
            {
                Console.WriteLine("🔍 Testing foreign key constraint fix in FormService...");
                
                // Test the problematic scenario that should now be fixed
                await TestInitializeFormSessionWithInMemoryDb();
                
                Console.WriteLine("✅ Foreign key constraint fix validation successful");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Test failed with exception: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
                if (ex.InnerException != null)
                {
                    Console.WriteLine($"Inner exception: {ex.InnerException.Message}");
                }
                return false;
            }
        }
        
        private static async Task TestInitializeFormSessionWithInMemoryDb()
        {
            // Create in-memory database for testing
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
                .Options;

            using var context = new ApplicationDbContext(options);
            
            // Set up mocks for dependencies
            var mockEmailService = new Mock<IEmailService>();
            var mockPdfService = new Mock<IPdfGenerationService>();
            var mockBlobService = new Mock<IBlobStorageService>();
            var mockDebugConsole = new Mock<IDebugConsoleHelper>();
            var mockLogger = new Mock<ILogger<FormService>>();
            
            var appSettings = new ApplicationSettings
            {
                TokenExpirationMinutes = 10,
                TokenLength = 6
            };
            var mockOptions = new Mock<IOptions<ApplicationSettings>>();
            mockOptions.Setup(x => x.Value).Returns(appSettings);

            // Create FormService instance
            var formService = new FormService(
                context,
                mockEmailService.Object,
                mockPdfService.Object,
                mockBlobService.Object,
                mockOptions.Object,
                mockLogger.Object,
                mockDebugConsole.Object
            );

            // Test: This should not throw a foreign key constraint exception
            var result = await formService.InitializeFormSessionAsync("test@example.com");
            
            // Verify the result is successful
            if (!result.Success)
            {
                throw new Exception($"Form session initialization failed: {result.Message}");
            }
            
            // Verify that both submission and log were saved correctly
            var submission = await context.FormSubmissions
                .Include(s => s.Logs)
                .FirstOrDefaultAsync(s => s.SubmissionId == result.SubmissionId);
                
            if (submission == null)
            {
                throw new Exception("Submission was not saved to database");
            }
            
            if (submission.Logs.Count == 0)
            {
                throw new Exception("Submission log was not saved to database");
            }
            
            Console.WriteLine($"✓ Form session initialized successfully with ID: {result.SubmissionId}");
            Console.WriteLine($"✓ Submission entity saved with ID: {submission.Id}");
            Console.WriteLine($"✓ Log entries created: {submission.Logs.Count}");
        }
        
        public static async Task Main(string[] args)
        {
            var result = await TestForeignKeyConstraintFix();
            Environment.Exit(result ? 0 : 1);
        }
    }
    

}