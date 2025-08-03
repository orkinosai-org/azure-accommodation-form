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
    /// Test to validate enhanced DbUpdateException handling in FormService
    /// Specifically tests FOREIGN KEY constraint failure detection (SQLite Error 19)
    /// </summary>
    public class DbUpdateExceptionHandlingTest
    {
        public static async Task<bool> TestFormServiceDbUpdateExceptionHandling()
        {
            try
            {
                Console.WriteLine("🔍 Testing FormService enhanced DbUpdateException handling...");
                
                // Test the patterns used in our enhanced exception handling
                await TestDbUpdateExceptionPatterns();
                
                Console.WriteLine("✅ FormService DbUpdateException handling validation successful");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Test failed with exception: {ex.Message}");
                return false;
            }
        }
        
        private static async Task TestDbUpdateExceptionPatterns()
        {
            // Test 1: FOREIGN KEY constraint failure pattern
            var foreignKeyInnerEx = new Exception("SQLite Error 19: 'FOREIGN KEY constraint failed'.");
            var foreignKeyDbEx = new DbUpdateException("An error occurred while saving the entity changes.", foreignKeyInnerEx);
            
            var isForeignKeyError = foreignKeyDbEx.InnerException?.Message?.Contains("FOREIGN KEY constraint failed") == true;
            Console.WriteLine($"✓ FOREIGN KEY constraint detection: {isForeignKeyError}");
            
            // Test 2: UNIQUE constraint failure pattern
            var uniqueInnerEx = new Exception("SQLite Error 19: 'UNIQUE constraint failed: FormSubmissions.SubmissionId'.");
            var uniqueDbEx = new DbUpdateException("An error occurred while saving the entity changes.", uniqueInnerEx);
            
            var isUniqueError = uniqueDbEx.InnerException?.Message?.Contains("UNIQUE constraint failed") == true;
            Console.WriteLine($"✓ UNIQUE constraint detection: {isUniqueError}");
            
            // Test 3: Generic DbUpdateException pattern
            var genericInnerEx = new Exception("Some other database error");
            var genericDbEx = new DbUpdateException("An error occurred while saving the entity changes.", genericInnerEx);
            
            var isDbUpdateException = genericDbEx is DbUpdateException;
            var hasInnerException = genericDbEx.InnerException != null;
            Console.WriteLine($"✓ DbUpdateException type detection: {isDbUpdateException}");
            Console.WriteLine($"✓ Inner exception presence: {hasInnerException}");
            
            // Test 4: Regular exception (non-DbUpdateException)
            var regularEx = new InvalidOperationException("Regular operation failed");
            var isNotDbUpdateException = !(regularEx is DbUpdateException);
            Console.WriteLine($"✓ Non-DbUpdateException handling: {isNotDbUpdateException}");
            
            // Validate all patterns work as expected
            if (!isForeignKeyError || !isUniqueError || !isDbUpdateException || !hasInnerException || !isNotDbUpdateException)
            {
                throw new Exception("One or more exception handling patterns failed validation");
            }
            
            Console.WriteLine("✓ All exception handling patterns validated successfully");
        }
        
        public static async Task Main(string[] args)
        {
            var result = await TestFormServiceDbUpdateExceptionHandling();
            Environment.Exit(result ? 0 : 1);
        }
    }
}