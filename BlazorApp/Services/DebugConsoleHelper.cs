using Microsoft.JSInterop;

namespace BlazorApp.Services;

public interface IDebugConsoleHelper
{
    Task LogAsync(string message, string level = "log");
    Task LogInfoAsync(string message);
    Task LogWarningAsync(string message);
    Task LogErrorAsync(string message);
    Task LogGroupAsync(string groupName);
    Task LogGroupEndAsync();
}

public class DebugConsoleHelper : IDebugConsoleHelper
{
    private readonly IJSRuntime _jsRuntime;
    private readonly ILogger<DebugConsoleHelper> _logger;

    public DebugConsoleHelper(IJSRuntime jsRuntime, ILogger<DebugConsoleHelper> logger)
    {
        _jsRuntime = jsRuntime;
        _logger = logger;
    }

    public async Task LogAsync(string message, string level = "log")
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("debugConsole.log", message, level);
        }
        catch (Exception ex)
        {
            // Fallback to server-side logging if JS interop fails
            _logger.LogWarning(ex, "Failed to log to browser console: {Message}", message);
        }
    }

    public async Task LogInfoAsync(string message)
    {
        await LogAsync(message, "info");
    }

    public async Task LogWarningAsync(string message)
    {
        await LogAsync(message, "warn");
    }

    public async Task LogErrorAsync(string message)
    {
        await LogAsync(message, "error");
    }

    public async Task LogGroupAsync(string groupName)
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("debugConsole.group", groupName);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to start console group: {GroupName}", groupName);
        }
    }

    public async Task LogGroupEndAsync()
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("debugConsole.groupEnd");
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to end console group");
        }
    }
}