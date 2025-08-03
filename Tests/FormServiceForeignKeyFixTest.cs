using Microsoft.EntityFrameworkCore;
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
    /// Focused test to verify the foreign key constraint fix in FormService
    /// </summary>
    public class FormServiceForeignKeyFixTest
    {
        public static async Task<bool> TestFormServiceForeignKeyFix()
        {
            try
            {
                Console.WriteLine("🔍 Testing FormService foreign key constraint fix...");
                
                // Test InitializeFormSessionAsync with SQLite database
                await TestInitializeFormSessionAsync();
                
                // Test ProcessFormDirectAsync
                await TestProcessFormDirectAsync();
                
                Console.WriteLine("✅ FormService foreign key constraint fix validation successful");
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
        
        private static async Task TestInitializeFormSessionAsync()
        {
            Console.WriteLine("🧪 Testing InitializeFormSessionAsync...");
            
            // Create SQLite database file for more reliable testing
            var dbPath = Path.Combine(Path.GetTempPath(), $"test_init_{Guid.NewGuid()}.db");
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseSqlite($"Data Source={dbPath}")
                .Options;

            using var context = new ApplicationDbContext(options);
            await context.Database.EnsureCreatedAsync();
            
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

            // Test: This should NOT throw a foreign key constraint exception anymore
            var result = await formService.InitializeFormSessionAsync("test@example.com");
            
            // Verify the result is successful
            if (!result.Success)
            {
                Console.WriteLine($"❌ Result Success: {result.Success}");
                Console.WriteLine($"❌ Result Message: {result.Message}");
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
            
            var log = submission.Logs.First();
            if (log.Action != "SessionInitialized")
            {
                throw new Exception($"Expected log action 'SessionInitialized', but got '{log.Action}'");
            }
            
            Console.WriteLine($"✓ InitializeFormSessionAsync: Session initialized with ID: {result.SubmissionId}");
            Console.WriteLine($"✓ InitializeFormSessionAsync: Submission entity saved with ID: {submission.Id}");
            Console.WriteLine($"✓ InitializeFormSessionAsync: Log entries created: {submission.Logs.Count}");
            Console.WriteLine($"✓ InitializeFormSessionAsync: Log action: {log.Action}");
            
            // Cleanup test database
            context.Dispose();
            if (File.Exists(dbPath))
            {
                File.Delete(dbPath);
            }
        }
        
        private static async Task TestProcessFormDirectAsync()
        {
            Console.WriteLine("🧪 Testing ProcessFormDirectAsync...");
            
            // Create SQLite database file for more reliable testing
            var dbPath = Path.Combine(Path.GetTempPath(), $"test_direct_{Guid.NewGuid()}.db");
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseSqlite($"Data Source={dbPath}")
                .Options;

            using var context = new ApplicationDbContext(options);
            await context.Database.EnsureCreatedAsync();
            
            // Set up mocks for dependencies
            var mockEmailService = new Mock<IEmailService>();
            var mockPdfService = new Mock<IPdfGenerationService>();
            var mockBlobService = new Mock<IBlobStorageService>();
            var mockDebugConsole = new Mock<IDebugConsoleHelper>();
            var mockLogger = new Mock<ILogger<FormService>>();
            
            // Setup mock returns for services
            mockPdfService.Setup(x => x.GenerateFormPdfAsync(It.IsAny<FormData>(), It.IsAny<string>(), It.IsAny<DateTime>(), It.IsAny<string>()))
                .ReturnsAsync(new byte[] { 1, 2, 3 });
            mockPdfService.Setup(x => x.GenerateFileName(It.IsAny<FormData>(), It.IsAny<DateTime>()))
                .Returns("test.pdf");
            mockBlobService.Setup(x => x.UploadFormPdfAsync(It.IsAny<byte[]>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync("https://test.blob.url/test.pdf");
            mockEmailService.Setup(x => x.SendFormSubmissionConfirmationAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<byte[]>(), It.IsAny<string>()))
                .ReturnsAsync(true);
            mockEmailService.Setup(x => x.SendFormSubmissionToCompanyAsync(It.IsAny<string>(), It.IsAny<byte[]>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(true);
            
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

            // Create test form data
            var formData = new FormData
            {
                TenantDetails = new TenantDetails
                {
                    Email = "test@example.com",
                    FullName = "Test User"
                }
            };

            // Test: This should NOT throw a foreign key constraint exception anymore
            var result = await formService.ProcessFormDirectAsync(formData, "127.0.0.1");
            
            // Verify the result is successful
            if (!result.Success)
            {
                throw new Exception($"Process form direct failed: {result.Message}");
            }
            
            // Verify that both submission and logs were saved correctly
            var submission = await context.FormSubmissions
                .Include(s => s.Logs)
                .FirstOrDefaultAsync(s => s.SubmissionId == result.SubmissionId);
                
            if (submission == null)
            {
                throw new Exception("Submission was not saved to database");
            }
            
            if (submission.Logs.Count == 0)
            {
                throw new Exception("Submission logs were not saved to database");
            }
            
            var directSubmissionLog = submission.Logs.FirstOrDefault(l => l.Action == "DirectSubmission");
            if (directSubmissionLog == null)
            {
                throw new Exception("DirectSubmission log entry not found");
            }
            
            Console.WriteLine($"✓ ProcessFormDirectAsync: Form processed with ID: {result.SubmissionId}");
            Console.WriteLine($"✓ ProcessFormDirectAsync: Submission entity saved with ID: {submission.Id}");
            Console.WriteLine($"✓ ProcessFormDirectAsync: Log entries created: {submission.Logs.Count}");
            Console.WriteLine($"✓ ProcessFormDirectAsync: DirectSubmission log found: {directSubmissionLog.Details}");
            
            // Cleanup test database
            context.Dispose();
            if (File.Exists(dbPath))
            {
                File.Delete(dbPath);
            }
        }
        
        public static async Task Main(string[] args)
        {
            var result = await TestFormServiceForeignKeyFix();
            Environment.Exit(result ? 0 : 1);
        }
    }
}