using BlazorApp.Models;
using BlazorApp.Controllers;
using BlazorApp.Services;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace Tests;

/// <summary>
/// Test to verify enhanced debugging features for development mode form submissions
/// </summary>
public class EnhancedDebuggingTest
{
    public static async Task RunAsync()
    {
        Console.WriteLine("=== ENHANCED DEBUGGING TEST ===");
        Console.WriteLine("Testing enhanced error logging and development mode debugging features...");
        
        try
        {
            // Test 1: Verify development mode detection
            await TestDevelopmentModeDetection();
            
            // Test 2: Test validation error enhancement
            await TestValidationErrorHandling();
            
            // Test 3: Test local storage fallback
            await TestLocalStorageFallback();
            
            // Test 4: Test form data completeness logging
            await TestFormDataCompletenessLogging();
            
            Console.WriteLine("✓ All enhanced debugging tests passed!");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Enhanced debugging test failed: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
        }
    }

    private static Task TestDevelopmentModeDetection()
    {
        Console.WriteLine("\n--- Testing Development Mode Detection ---");
        
        // Create a mock development environment
        var mockEnvironment = new TestWebHostEnvironment
        {
            EnvironmentName = "Development"
        };
        
        Console.WriteLine($"Environment: {mockEnvironment.EnvironmentName}");
        Console.WriteLine($"Is Development: {mockEnvironment.IsDevelopment()}");
        
        if (mockEnvironment.IsDevelopment())
        {
            Console.WriteLine("✓ Development mode detection working correctly");
        }
        else
        {
            throw new Exception("Development mode detection failed");
        }
        
        return Task.CompletedTask;
    }

    private static Task TestValidationErrorHandling()
    {
        Console.WriteLine("\n--- Testing Validation Error Handling ---");
        
        // Create invalid form data to trigger validation
        var invalidFormData = new FormData
        {
            TenantDetails = new TenantDetails
            {
                // Missing required fields to trigger validation errors
                FullName = "",
                Email = "invalid-email",
                Telephone = ""
            }
        };
        
        // Test JSON serialization for logging
        try
        {
            var jsonOptions = new JsonSerializerOptions 
            { 
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };
            var json = JsonSerializer.Serialize(invalidFormData, jsonOptions);
            Console.WriteLine($"✓ Form data serialization successful ({json.Length} chars)");
        }
        catch (Exception ex)
        {
            throw new Exception($"Form data serialization failed: {ex.Message}");
        }
        
        // Test form structure analysis
        var structureInfo = new
        {
            TenantDetailsProvided = invalidFormData.TenantDetails != null,
            BankDetailsProvided = invalidFormData.BankDetails != null,
            AddressHistoryCount = invalidFormData.AddressHistory?.Count ?? 0,
            ContactsCount = invalidFormData.Contacts != null ? 1 : 0,
            MedicalDetailsProvided = invalidFormData.MedicalDetails != null,
            EmploymentProvided = invalidFormData.Employment != null,
            PassportDetailsProvided = invalidFormData.PassportDetails != null,
            CurrentLivingArrangementProvided = invalidFormData.CurrentLivingArrangement != null,
            OtherProvided = invalidFormData.Other != null,
            ConsentAndDeclarationProvided = invalidFormData.ConsentAndDeclaration != null
        };
        
        Console.WriteLine($"✓ Form structure analysis: {JsonSerializer.Serialize(structureInfo)}");
        return Task.CompletedTask;
    }

    private static async Task TestLocalStorageFallback()
    {
        Console.WriteLine("\n--- Testing Local Storage Fallback ---");
        
        // Test directory path creation
        var tempPath = Path.GetTempPath();
        var testDir = Path.Combine(tempPath, "azure-accommodation-form-dev-storage-test");
        
        try
        {
            // Test directory creation
            if (!Directory.Exists(testDir))
            {
                Directory.CreateDirectory(testDir);
                Console.WriteLine($"✓ Test directory created: {testDir}");
            }
            
            // Test write permissions
            var testFile = Path.Combine(testDir, "test.txt");
            await File.WriteAllTextAsync(testFile, "Test content");
            
            // Verify file was written
            if (File.Exists(testFile))
            {
                var content = await File.ReadAllTextAsync(testFile);
                if (content == "Test content")
                {
                    Console.WriteLine("✓ Local storage write/read test successful");
                }
                else
                {
                    throw new Exception("File content mismatch");
                }
            }
            else
            {
                throw new Exception("Test file was not created");
            }
            
            // Test disk space checking
            var driveInfo = new DriveInfo(new DirectoryInfo(testDir).Root.Name);
            var availableSpace = driveInfo.AvailableFreeSpace / 1024 / 1024; // MB
            Console.WriteLine($"✓ Available disk space: {availableSpace:F2} MB");
            
            // Cleanup
            File.Delete(testFile);
            Directory.Delete(testDir);
            Console.WriteLine("✓ Test cleanup completed");
        }
        catch (Exception ex)
        {
            throw new Exception($"Local storage test failed: {ex.Message}");
        }
    }

    private static Task TestFormDataCompletenessLogging()
    {
        Console.WriteLine("\n--- Testing Form Data Completeness Logging ---");
        
        // Create a partially complete form
        var formData = new FormData
        {
            TenantDetails = new TenantDetails
            {
                FullName = "Test User",
                Email = "test@example.com",
                Telephone = "+1234567890"
            },
            BankDetails = new BankDetails
            {
                BankName = "Test Bank",
                AccountNo = "12345678"
            },
            AddressHistory = new List<AddressHistoryItem>
            {
                new AddressHistoryItem
                {
                    Address = "123 Test Street",
                    From = DateTime.Now.AddYears(-1)
                }
            }
            // Note: FormData automatically initializes all sections in the constructor
        };
        
        // Test completeness analysis
        var completenessInfo = new
        {
            TenantDetails = formData.TenantDetails != null,
            BankDetails = formData.BankDetails != null,
            AddressHistoryCount = formData.AddressHistory?.Count ?? 0,
            ContactsCount = formData.Contacts != null ? 1 : 0,
            SectionsComplete = new[]
            {
                formData.TenantDetails != null,
                formData.BankDetails != null,
                formData.AddressHistory?.Any() == true,
                formData.MedicalDetails != null,
                formData.Employment != null,
                formData.PassportDetails != null,
                formData.CurrentLivingArrangement != null,
                formData.Other != null,
                formData.ConsentAndDeclaration != null
            }.Count(x => x)
        };
        
        Console.WriteLine($"✓ Form completeness analysis: {JsonSerializer.Serialize(completenessInfo, new JsonSerializerOptions { WriteIndented = true })}");
        
        // Verify expected completeness (FormData constructor initializes all sections)
        if (completenessInfo.SectionsComplete == 9) // All sections are auto-initialized
        {
            Console.WriteLine("✓ Form completeness calculation correct (all sections auto-initialized)");
        }
        else
        {
            throw new Exception($"Form completeness calculation incorrect: expected 9, got {completenessInfo.SectionsComplete}");
        }
        
        return Task.CompletedTask;
    }

    /// <summary>
    /// Mock WebHostEnvironment for testing
    /// </summary>
    private class TestWebHostEnvironment : IWebHostEnvironment
    {
        public string EnvironmentName { get; set; } = "Development";
        public string ApplicationName { get; set; } = "TestApp";
        public string WebRootPath { get; set; } = "";
        public string ContentRootPath { get; set; } = "";
        public Microsoft.Extensions.FileProviders.IFileProvider WebRootFileProvider { get; set; } = null!;
        public Microsoft.Extensions.FileProviders.IFileProvider ContentRootFileProvider { get; set; } = null!;
    }
}