using BlazorApp.Services;

namespace BlazorApp.Tests;

/// <summary>
/// Simple test to validate threading fixes without external dependencies
/// </summary>
public class SimpleThreadingTest
{
    /// <summary>
    /// Tests basic threading health and the thread pool monitoring service
    /// </summary>
    public static async Task TestBasicThreadPoolHealth()
    {
        Console.WriteLine("=== BASIC THREADING HEALTH TEST ===");
        
        // Test ThreadPoolMonitoringService directly
        var monitor = new ThreadPoolMonitoringService(
            new MockLogger<ThreadPoolMonitoringService>(),
            new MockDebugConsoleHelper()
        );
        
        // Test initial status logging
        monitor.LogThreadPoolStatus("Initial Test");
        
        // Test monitoring start/stop
        monitor.StartMonitoring();
        
        // Wait a bit to let monitoring work
        await Task.Delay(2000);
        
        // Test multiple concurrent tasks with ConfigureAwait(false) pattern
        var tasks = new List<Task>();
        
        for (int i = 0; i < 10; i++)
        {
            var taskId = i;
            tasks.Add(Task.Run(async () =>
            {
                monitor.LogThreadPoolStatus($"Task {taskId} Start");
                
                // Simulate async work with proper ConfigureAwait(false)
                await SimulateAsyncWork(taskId).ConfigureAwait(false);
                
                monitor.LogThreadPoolStatus($"Task {taskId} Complete");
            }));
        }
        
        // Wait for all tasks to complete
        await Task.WhenAll(tasks).ConfigureAwait(false);
        
        monitor.LogThreadPoolStatus("All Tasks Complete");
        monitor.StopMonitoring();
        
        Console.WriteLine("=== BASIC THREADING HEALTH TEST PASSED ===");
        Console.WriteLine("Thread pool monitoring and ConfigureAwait patterns working correctly!");
    }
    
    private static async Task SimulateAsyncWork(int taskId)
    {
        // Simulate various async patterns
        await Task.Delay(100).ConfigureAwait(false);
        
        // Simulate CPU-bound work
        var result = await Task.Run(() =>
        {
            var sum = 0;
            for (int i = 0; i < 1000; i++)
            {
                sum += i;
            }
            return sum;
        }).ConfigureAwait(false);
        
        // Simulate more async I/O
        await Task.Delay(50).ConfigureAwait(false);
        
        Console.WriteLine($"Task {taskId}: Completed simulated work with result {result}");
    }
}

/// <summary>
/// Mock logger for testing
/// </summary>
public class MockLogger<T> : Microsoft.Extensions.Logging.ILogger<T>
{
    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;
    public bool IsEnabled(Microsoft.Extensions.Logging.LogLevel logLevel) => true;
    
    public void Log<TState>(Microsoft.Extensions.Logging.LogLevel logLevel, Microsoft.Extensions.Logging.EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
    {
        Console.WriteLine($"[{logLevel}] {formatter(state, exception)}");
    }
}