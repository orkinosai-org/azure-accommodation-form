using BlazorApp.Tests;

namespace Tests
{
    /// <summary>
    /// Test runner for threading validation
    /// </summary>
    public class ThreadingTestRunner
    {
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Starting Threading Fix Validation Test...");
            
            try
            {
                // Run basic threading health test first
                await SimpleThreadingTest.TestBasicThreadPoolHealth();
                
                Console.WriteLine("\nThreading tests completed successfully!");
                Environment.Exit(0);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Threading test failed: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
                Environment.Exit(1);
            }
        }
    }
}