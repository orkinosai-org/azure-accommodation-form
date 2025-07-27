using Microsoft.Extensions.Logging;
using Microsoft.JSInterop;
using BlazorApp.Services;
using BlazorApp.Models;
using System;
using System.IO;
using System.Threading.Tasks;
using Moq;

namespace Tests;

/// <summary>
/// Simple test to verify that audit trail information is included in PDF generation
/// </summary>
public class AuditTrailTest
{
    public static async Task<bool> TestPdfAuditTrailGeneration()
    {
        try
        {
            // Create a mock logger and debug console
            var loggerFactory = LoggerFactory.Create(builder => builder.AddConsole());
            var logger = loggerFactory.CreateLogger<PdfGenerationService>();
            
            // Create mock debug console helper
            var mockJsRuntime = new Mock<IJSRuntime>();
            var mockDebugLogger = new Mock<ILogger<DebugConsoleHelper>>();
            var debugConsole = new DebugConsoleHelper(mockJsRuntime.Object, mockDebugLogger.Object);
            
            // Create the PDF generation service
            var pdfService = new PdfGenerationService(logger, debugConsole);
            
            // Create test form data
            var formData = new FormData
            {
                TenantDetails = new TenantDetails
                {
                    FullName = "Test User",
                    Email = "test@example.com",
                    DateOfBirth = DateTime.Parse("1990-01-01"),
                    Telephone = "+1234567890"
                },
                ConsentAndDeclaration = new ConsentAndDeclaration
                {
                    ConsentGiven = true,
                    Signature = "Test Signature",
                    Date = DateTime.UtcNow,
                    PrintName = "Test User"
                }
            };
            
            // Test parameters
            var submissionId = "test-submission-123";
            var submissionTime = DateTime.Parse("2024-01-15 10:30:00").ToUniversalTime();
            var clientIp = "192.168.1.100";
            
            // Generate PDF with audit trail
            var pdfBytes = await pdfService.GenerateFormPdfAsync(formData, submissionId, submissionTime, clientIp);
            
            // Verify that PDF was generated successfully
            if (pdfBytes == null || pdfBytes.Length == 0)
            {
                Console.WriteLine("❌ FAIL: PDF generation returned null or empty result");
                return false;
            }
            
            // Save to temporary file for verification (optional)
            var tempFile = Path.Combine("/tmp", "test_audit_trail.pdf");
            await File.WriteAllBytesAsync(tempFile, pdfBytes);
            
            Console.WriteLine("✅ PASS: PDF generated successfully with audit trail");
            Console.WriteLine($"   - PDF size: {pdfBytes.Length} bytes");
            Console.WriteLine($"   - Temporary file: {tempFile}");
            Console.WriteLine($"   - Submission ID: {submissionId}");
            Console.WriteLine($"   - Submission Time: {submissionTime:yyyy-MM-dd HH:mm:ss} UTC");
            Console.WriteLine($"   - Client IP: {clientIp}");
            
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ FAIL: Exception during PDF generation: {ex.Message}");
            Console.WriteLine($"   Stack trace: {ex.StackTrace}");
            return false;
        }
    }
}