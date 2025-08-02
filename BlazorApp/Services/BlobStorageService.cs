using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Microsoft.Extensions.Options;

namespace BlazorApp.Services;

public interface IBlobStorageService
{
    Task<string> UploadFormPdfAsync(byte[] pdfData, string fileName, string submissionId);
    Task<bool> DeleteFormPdfAsync(string blobUrl);
}

public class BlobStorageService : IBlobStorageService
{
    private readonly BlobStorageSettings _settings;
    private readonly ILogger<BlobStorageService> _logger;
    private readonly BlobServiceClient _blobServiceClient;
    private readonly IDebugConsoleHelper _debugConsole;

    public BlobStorageService(
        IOptions<BlobStorageSettings> settings,
        ILogger<BlobStorageService> logger,
        IDebugConsoleHelper debugConsole)
    {
        _settings = settings.Value;
        _logger = logger;
        _debugConsole = debugConsole;
        _blobServiceClient = new BlobServiceClient(_settings.ConnectionString);
    }

    public async Task<string> UploadFormPdfAsync(byte[] pdfData, string fileName, string submissionId)
    {
        try
        {
            // Mask connection string secrets
            var maskedConnectionString = MaskConnectionString(_settings.ConnectionString);

            // DEBUG: Log blob storage configuration to browser console (production: remove this section)
            await _debugConsole.LogGroupAsync("BLOB STORAGE DEBUG INFO").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Container Name: {_settings.ContainerName}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Connection String: {maskedConnectionString}").ConfigureAwait(false);
            await _debugConsole.LogGroupEndAsync().ConfigureAwait(false);

            // DEBUG: Log blob storage configuration (production: remove this section)
            Console.WriteLine("=== BLOB STORAGE DEBUG INFO ===");
            Console.WriteLine($"Container Name: {_settings.ContainerName}");
            Console.WriteLine($"Connection String: {maskedConnectionString}");

            _logger.LogInformation("DEBUG - Blob storage configuration: Container={ContainerName}, ConnectionString={MaskedConnectionString}",
                _settings.ContainerName, maskedConnectionString);

            var containerClient = await GetContainerClientAsync().ConfigureAwait(false);
            var blobName = $"{submissionId}/{fileName}";
            var blobClient = containerClient.GetBlobClient(blobName);

            // DEBUG: Log blob upload details to browser console (production: remove this section)
            await _debugConsole.LogGroupAsync("BLOB UPLOAD DEBUG").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Blob Name: {blobName}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"File Size: {pdfData.Length} bytes").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Submission ID: {submissionId}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Target URI: {blobClient.Uri}").ConfigureAwait(false);
            await _debugConsole.LogGroupEndAsync().ConfigureAwait(false);

            // DEBUG: Log blob upload details (production: remove this section)
            Console.WriteLine("=== BLOB UPLOAD DEBUG ===");
            Console.WriteLine($"Blob Name: {blobName}");
            Console.WriteLine($"File Size: {pdfData.Length} bytes");
            Console.WriteLine($"Submission ID: {submissionId}");
            Console.WriteLine($"Target URI: {blobClient.Uri}");

            _logger.LogInformation("DEBUG - Blob upload: BlobName={BlobName}, FileSize={FileSize}, SubmissionId={SubmissionId}",
                blobName, pdfData.Length, submissionId);

            using var stream = new MemoryStream(pdfData);
            
            var options = new BlobUploadOptions
            {
                HttpHeaders = new BlobHttpHeaders
                {
                    ContentType = "application/pdf"
                },
                Metadata = new Dictionary<string, string>
                {
                    { "SubmissionId", submissionId },
                    { "UploadedAt", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ") },
                    { "FileType", "FormSubmissionPdf" }
                }
            };

            await blobClient.UploadAsync(stream, options).ConfigureAwait(false);

            // DEBUG: Log successful upload to browser console (production: remove this section)
            await _debugConsole.LogInfoAsync("BLOB UPLOADED SUCCESSFULLY").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Blob URL: {blobClient.Uri}").ConfigureAwait(false);

            // DEBUG: Log successful upload (production: remove this section)
            Console.WriteLine("=== BLOB UPLOADED SUCCESSFULLY ===");
            Console.WriteLine($"Blob URL: {blobClient.Uri}");

            _logger.LogInformation("Successfully uploaded PDF {FileName} for submission {SubmissionId}", fileName, submissionId);
            _logger.LogInformation("DEBUG - Blob uploaded successfully to: {BlobUrl}", blobClient.Uri);
            
            return blobClient.Uri.ToString();
        }
        catch (Exception ex)
        {
            // DEBUG: Enhanced error logging to browser console (production: keep but remove DEBUG prefix)
            await _debugConsole.LogErrorAsync("BLOB UPLOAD FAILED").ConfigureAwait(false);
            await _debugConsole.LogErrorAsync($"Error: {ex.Message}").ConfigureAwait(false);

            // DEBUG: Enhanced error logging (production: keep but remove DEBUG prefix)
            Console.WriteLine($"=== BLOB UPLOAD FAILED ===");
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            
            _logger.LogError(ex, "Failed to upload PDF {FileName} for submission {SubmissionId}", fileName, submissionId);
            throw;
        }
    }

    public async Task<bool> DeleteFormPdfAsync(string blobUrl)
    {
        try
        {
            var uri = new Uri(blobUrl);
            var blobName = uri.AbsolutePath.TrimStart('/').Substring(_settings.ContainerName.Length + 1);
            
            // Mask connection string secrets
            var maskedConnectionString = MaskConnectionString(_settings.ConnectionString);

            // DEBUG: Log blob deletion details to browser console (production: remove this section)
            await _debugConsole.LogGroupAsync("BLOB DELETE DEBUG").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Container Name: {_settings.ContainerName}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Connection String: {maskedConnectionString}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Blob URL: {blobUrl}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Blob Name: {blobName}").ConfigureAwait(false);
            await _debugConsole.LogGroupEndAsync().ConfigureAwait(false);

            // DEBUG: Log blob deletion details (production: remove this section)
            Console.WriteLine("=== BLOB DELETE DEBUG ===");
            Console.WriteLine($"Container Name: {_settings.ContainerName}");
            Console.WriteLine($"Connection String: {maskedConnectionString}");
            Console.WriteLine($"Blob URL: {blobUrl}");
            Console.WriteLine($"Blob Name: {blobName}");

            _logger.LogInformation("DEBUG - Blob deletion: ContainerName={ContainerName}, BlobName={BlobName}, BlobUrl={BlobUrl}",
                _settings.ContainerName, blobName, blobUrl);
            
            var containerClient = await GetContainerClientAsync().ConfigureAwait(false);
            var blobClient = containerClient.GetBlobClient(blobName);

            var response = await blobClient.DeleteIfExistsAsync().ConfigureAwait(false);
            
            if (response.Value)
            {
                // DEBUG: Log successful deletion to browser console (production: remove this section)
                await _debugConsole.LogInfoAsync("BLOB DELETED SUCCESSFULLY").ConfigureAwait(false);
                await _debugConsole.LogAsync($"Deleted blob: {blobUrl}").ConfigureAwait(false);

                // DEBUG: Log successful deletion (production: remove this section)
                Console.WriteLine("=== BLOB DELETED SUCCESSFULLY ===");
                Console.WriteLine($"Deleted blob: {blobUrl}");

                _logger.LogInformation("Successfully deleted PDF blob: {BlobUrl}", blobUrl);
                _logger.LogInformation("DEBUG - Blob deleted successfully: {BlobUrl}", blobUrl);
            }
            else
            {
                // DEBUG: Log blob not found to browser console (production: remove this section)
                await _debugConsole.LogWarningAsync("BLOB NOT FOUND FOR DELETION").ConfigureAwait(false);
                await _debugConsole.LogAsync($"Blob not found: {blobUrl}").ConfigureAwait(false);

                // DEBUG: Log blob not found (production: remove this section)
                Console.WriteLine("=== BLOB NOT FOUND FOR DELETION ===");
                Console.WriteLine($"Blob not found: {blobUrl}");

                _logger.LogWarning("Blob not found for deletion: {BlobUrl}", blobUrl);
            }
            
            return response.Value;
        }
        catch (Exception ex)
        {
            // DEBUG: Enhanced error logging to browser console (production: keep but remove DEBUG prefix)
            await _debugConsole.LogErrorAsync("BLOB DELETE FAILED").ConfigureAwait(false);
            await _debugConsole.LogErrorAsync($"Error: {ex.Message}").ConfigureAwait(false);

            // DEBUG: Enhanced error logging (production: keep but remove DEBUG prefix)
            Console.WriteLine($"=== BLOB DELETE FAILED ===");
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");

            _logger.LogError(ex, "Failed to delete PDF blob: {BlobUrl}", blobUrl);
            return false;
        }
    }

    private async Task<BlobContainerClient> GetContainerClientAsync()
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(_settings.ContainerName);
        await containerClient.CreateIfNotExistsAsync(PublicAccessType.None).ConfigureAwait(false);
        return containerClient;
    }

    // DEBUG: Helper method to mask sensitive information in connection string (production: remove this method)
    private string MaskConnectionString(string connectionString)
    {
        if (string.IsNullOrEmpty(connectionString))
            return "***NOT SET***";

        // Look for AccountKey and SharedAccessSignature patterns and mask them
        var masked = connectionString;
        
        // Mask AccountKey
        var accountKeyPattern = @"AccountKey=[^;]+";
        masked = System.Text.RegularExpressions.Regex.Replace(masked, accountKeyPattern, "AccountKey=***MASKED***");
        
        // Mask SharedAccessSignature
        var sasPattern = @"SharedAccessSignature=[^;]+";
        masked = System.Text.RegularExpressions.Regex.Replace(masked, sasPattern, "SharedAccessSignature=***MASKED***");
        
        return masked;
    }
}