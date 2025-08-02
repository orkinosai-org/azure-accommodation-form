using System.Diagnostics;

namespace BlazorApp.Services;

public interface IThreadPoolMonitoringService
{
    void LogThreadPoolStatus(string context);
    void StartMonitoring();
    void StopMonitoring();
}

public class ThreadPoolMonitoringService : IThreadPoolMonitoringService, IDisposable
{
    private readonly ILogger<ThreadPoolMonitoringService> _logger;
    private readonly IDebugConsoleHelper _debugConsole;
    private Timer? _monitoringTimer;
    private bool _disposed;

    public ThreadPoolMonitoringService(
        ILogger<ThreadPoolMonitoringService> logger,
        IDebugConsoleHelper debugConsole)
    {
        _logger = logger;
        _debugConsole = debugConsole;
    }

    public void LogThreadPoolStatus(string context)
    {
        try
        {
            ThreadPool.GetAvailableThreads(out int availableWorkerThreads, out int availableCompletionPortThreads);
            ThreadPool.GetMaxThreads(out int maxWorkerThreads, out int maxCompletionPortThreads);
            ThreadPool.GetMinThreads(out int minWorkerThreads, out int minCompletionPortThreads);

            var currentManagedThreadId = Environment.CurrentManagedThreadId;
            var isThreadPoolThread = Thread.CurrentThread.IsThreadPoolThread;
            var processId = Environment.ProcessId;
            var totalThreads = Process.GetCurrentProcess().Threads.Count;

            var status = new
            {
                Context = context,
                ProcessId = processId,
                CurrentManagedThreadId = currentManagedThreadId,
                IsThreadPoolThread = isThreadPoolThread,
                TotalSystemThreads = totalThreads,
                WorkerThreads = new
                {
                    Available = availableWorkerThreads,
                    InUse = maxWorkerThreads - availableWorkerThreads,
                    Max = maxWorkerThreads,
                    Min = minWorkerThreads
                },
                CompletionPortThreads = new
                {
                    Available = availableCompletionPortThreads,
                    InUse = maxCompletionPortThreads - availableCompletionPortThreads,
                    Max = maxCompletionPortThreads,
                    Min = minCompletionPortThreads
                }
            };

            _logger.LogInformation("ThreadPool Status: Context={Context}, ProcessId={ProcessId}, ThreadId={ThreadId}, " +
                "IsThreadPoolThread={IsThreadPoolThread}, TotalThreads={TotalThreads}, " +
                "WorkerThreads_Available={WorkerAvailable}, WorkerThreads_InUse={WorkerInUse}, " +
                "CompletionPortThreads_Available={CompletionAvailable}, CompletionPortThreads_InUse={CompletionInUse}",
                status.Context, status.ProcessId, status.CurrentManagedThreadId, status.IsThreadPoolThread,
                status.TotalSystemThreads, status.WorkerThreads.Available, status.WorkerThreads.InUse,
                status.CompletionPortThreads.Available, status.CompletionPortThreads.InUse);

            // Also log to console for debugging
            Console.WriteLine($"=== THREAD POOL STATUS: {context} ===");
            Console.WriteLine($"Process ID: {processId}");
            Console.WriteLine($"Current Thread ID: {currentManagedThreadId} (ThreadPool: {isThreadPoolThread})");
            Console.WriteLine($"Total System Threads: {totalThreads}");
            Console.WriteLine($"Worker Threads: {status.WorkerThreads.InUse}/{status.WorkerThreads.Max} (Available: {status.WorkerThreads.Available})");
            Console.WriteLine($"Completion Port Threads: {status.CompletionPortThreads.InUse}/{status.CompletionPortThreads.Max} (Available: {status.CompletionPortThreads.Available})");

            // Log potential issues
            if (status.WorkerThreads.Available < 5)
            {
                _logger.LogWarning("LOW WORKER THREAD AVAILABILITY: Only {AvailableThreads} worker threads available", status.WorkerThreads.Available);
                Console.WriteLine($"WARNING: Low worker thread availability: {status.WorkerThreads.Available}");
            }

            if (status.CompletionPortThreads.Available < 5)
            {
                _logger.LogWarning("LOW COMPLETION PORT THREAD AVAILABILITY: Only {AvailableThreads} completion port threads available", status.CompletionPortThreads.Available);
                Console.WriteLine($"WARNING: Low completion port thread availability: {status.CompletionPortThreads.Available}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to log thread pool status for context: {Context}", context);
            Console.WriteLine($"ERROR: Failed to log thread pool status: {ex.Message}");
        }
    }

    public void StartMonitoring()
    {
        if (_monitoringTimer != null)
            return;

        _logger.LogInformation("Starting thread pool monitoring");
        Console.WriteLine("Starting thread pool monitoring");

        _monitoringTimer = new Timer(state =>
        {
            LogThreadPoolStatus("Periodic Monitor");
        }, null, TimeSpan.Zero, TimeSpan.FromSeconds(30));
    }

    public void StopMonitoring()
    {
        _monitoringTimer?.Dispose();
        _monitoringTimer = null;

        _logger.LogInformation("Stopped thread pool monitoring");
        Console.WriteLine("Stopped thread pool monitoring");
    }

    public void Dispose()
    {
        if (_disposed)
            return;

        StopMonitoring();
        _disposed = true;
    }
}