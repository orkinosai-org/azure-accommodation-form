using Microsoft.Extensions.Logging;
using Microsoft.JSInterop;
using BlazorApp.Services;
using Moq;

namespace Tests;

/// <summary>
/// Test class to verify the DebugConsoleHelper functionality
/// This test ensures that the debug logging helper works correctly with JS interop
/// </summary>
public class DebugConsoleHelperTest
{
    public static async Task TestDebugConsoleHelper()
    {
        Console.WriteLine("=== DEBUG CONSOLE HELPER TEST ===");
        Console.WriteLine("Testing DebugConsoleHelper functionality...");

        // Create mock JS runtime
        var mockJsRuntime = new Mock<IJSRuntime>();
        var mockLogger = new Mock<ILogger<DebugConsoleHelper>>();

        // Setup JS runtime to capture InvokeAsync calls (simulate browser console)
        var jsCalls = new List<(string method, object[] args)>();
        mockJsRuntime
            .Setup(js => js.InvokeAsync<object>(It.IsAny<string>(), It.IsAny<CancellationToken>(), It.IsAny<object[]>()))
            .Returns(new ValueTask<object>(Task.FromResult<object>(null!)))
            .Callback<string, CancellationToken, object[]>((method, token, args) => 
            {
                jsCalls.Add((method, args));
                Console.WriteLine($"[SIMULATED BROWSER CONSOLE] {method}: {string.Join(", ", args)}");
            });

        // Create debug console helper
        var debugConsole = new DebugConsoleHelper(mockJsRuntime.Object, mockLogger.Object);

        // Test various logging methods
        Console.WriteLine("\n--- Testing Log Methods ---");
        await debugConsole.LogAsync("Test message", "log");
        await debugConsole.LogInfoAsync("Test info message");
        await debugConsole.LogWarningAsync("Test warning message");
        await debugConsole.LogErrorAsync("Test error message");

        Console.WriteLine("\n--- Testing Group Methods ---");
        await debugConsole.LogGroupAsync("Test Group");
        await debugConsole.LogAsync("Message inside group");
        await debugConsole.LogGroupEndAsync();

        // Verify calls were made
        Console.WriteLine($"\n--- Verification ---");
        Console.WriteLine($"Total JS interop calls made: {jsCalls.Count}");
        
        // Expected calls:
        // 1. LogAsync with "log" level
        // 2. LogInfoAsync 
        // 3. LogWarningAsync
        // 4. LogErrorAsync
        // 5. LogGroupAsync
        // 6. LogAsync inside group
        // 7. LogGroupEndAsync
        
        var expectedCalls = 7;
        if (jsCalls.Count == expectedCalls)
        {
            Console.WriteLine("✅ All expected JS interop calls were made");
        }
        else
        {
            Console.WriteLine($"❌ Expected {expectedCalls} calls, but got {jsCalls.Count}");
        }

        // Test specific method calls
        var debugConsoleCalls = jsCalls.Where(c => c.method.StartsWith("debugConsole.")).ToList();
        Console.WriteLine($"Debug console method calls: {debugConsoleCalls.Count}");

        foreach (var call in debugConsoleCalls)
        {
            Console.WriteLine($"  - {call.method}: {string.Join(", ", call.args)}");
        }

        Console.WriteLine("\n=== DEBUG CONSOLE HELPER TEST COMPLETED ===");
    }
}