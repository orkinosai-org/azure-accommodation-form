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
            await _debugConsole.LogGroupAsync("BLOB STORAGE DEBUG INFO");
            await _debugConsole.LogAsync($"Container Name: {_settings.ContainerName}");
            await _debugConsole.LogAsync($"Connection String: {maskedConnectionString}");
            await _debugConsole.LogGroupEndAsync();

            // DEBUG: Log blob storage configuration (production: remove this section)
            Console.WriteLine("=== BLOB STORAGE DEBUG INFO ===");
            Console.WriteLine($"Container Name: {_settings.ContainerName}");
            Console.WriteLine($"Connection String: {maskedConnectionString}");

            _logger.LogInformation("DEBUG - Blob storage configuration: Container={ContainerName}, ConnectionString={MaskedConnectionString}",
                _settings.ContainerName, maskedConnectionString);

            // Development storage fallback when Azurite is not available
            if (_settings.ConnectionString == "UseDevelopmentStorage=true")
            {
                return await UploadToLocalDevelopmentStorageAsync(pdfData, fileName, submissionId);
            }

            var containerClient = await GetContainerClientAsync();
            var blobName = $"{submissionId}/{fileName}";
            var blobClient = containerClient.GetBlobClient(blobName);

            // DEBUG: Log blob upload details to browser console (production: remove this section)
            await _debugConsole.LogGroupAsync("BLOB UPLOAD DEBUG");
            await _debugConsole.LogAsync($"Blob Name: {blobName}");
            await _debugConsole.LogAsync($"File Size: {pdfData.Length} bytes");
            await _debugConsole.LogAsync($"Submission ID: {submissionId}");
            await _debugConsole.LogAsync($"Target URI: {blobClient.Uri}");
            await _debugConsole.LogGroupEndAsync();

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

            await blobClient.UploadAsync(stream, options);

            // DEBUG: Log successful upload to browser console (production: remove this section)
            await _debugConsole.LogInfoAsync("BLOB UPLOADED SUCCESSFULLY");
            await _debugConsole.LogAsync($"Blob URL: {blobClient.Uri}");

            // DEBUG: Log successful upload (production: remove this section)
            Console.WriteLine("=== BLOB UPLOADED SUCCESSFULLY ===");
            Console.WriteLine($"Blob URL: {blobClient.Uri}");

            _logger.LogInformation("Successfully uploaded PDF {FileName} for submission {SubmissionId}", fileName, submissionId);
            _logger.LogInformation("DEBUG - Blob uploaded successfully to: {BlobUrl}", blobClient.Uri);
            
            return blobClient.Uri.ToString();
        }
        catch (Exception ex)
        {
            // Check if this is a development storage connection failure
            if (_settings.ConnectionString == "UseDevelopmentStorage=true" && 
                (ex.Message.Contains("Connection refused") || ex.Message.Contains("127.0.0.1:10000")))
            {
                _logger.LogWarning("Azure Storage Emulator (Azurite) not available, falling back to local file storage");
                
                // DEBUG: Log fallback to browser console (production: remove this section)
                await _debugConsole.LogWarningAsync("AZURITE NOT AVAILABLE - USING LOCAL FALLBACK");
                await _debugConsole.LogAsync("Azure Storage Emulator is not running, saving to local file system");
                
                Console.WriteLine("=== AZURITE NOT AVAILABLE - USING LOCAL FALLBACK ===");
                Console.WriteLine("Azure Storage Emulator is not running, saving to local file system");
                
                return await UploadToLocalDevelopmentStorageAsync(pdfData, fileName, submissionId);
            }

            // DEBUG: Enhanced error logging to browser console (production: keep but remove DEBUG prefix)
            await _debugConsole.LogErrorAsync("BLOB UPLOAD FAILED");
            await _debugConsole.LogErrorAsync($"Error: {ex.Message}");

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
            await _debugConsole.LogGroupAsync("BLOB DELETE DEBUG");
            await _debugConsole.LogAsync($"Container Name: {_settings.ContainerName}");
            await _debugConsole.LogAsync($"Connection String: {maskedConnectionString}");
            await _debugConsole.LogAsync($"Blob URL: {blobUrl}");
            await _debugConsole.LogAsync($"Blob Name: {blobName}");
            await _debugConsole.LogGroupEndAsync();

            // DEBUG: Log blob deletion details (production: remove this section)
            Console.WriteLine("=== BLOB DELETE DEBUG ===");
            Console.WriteLine($"Container Name: {_settings.ContainerName}");
            Console.WriteLine($"Connection String: {maskedConnectionString}");
            Console.WriteLine($"Blob URL: {blobUrl}");
            Console.WriteLine($"Blob Name: {blobName}");

            _logger.LogInformation("DEBUG - Blob deletion: ContainerName={ContainerName}, BlobName={BlobName}, BlobUrl={BlobUrl}",
                _settings.ContainerName, blobName, blobUrl);
            
            var containerClient = await GetContainerClientAsync();
            var blobClient = containerClient.GetBlobClient(blobName);

            var response = await blobClient.DeleteIfExistsAsync();
            
            if (response.Value)
            {
                // DEBUG: Log successful deletion to browser console (production: remove this section)
                await _debugConsole.LogInfoAsync("BLOB DELETED SUCCESSFULLY");
                await _debugConsole.LogAsync($"Deleted blob: {blobUrl}");

                // DEBUG: Log successful deletion (production: remove this section)
                Console.WriteLine("=== BLOB DELETED SUCCESSFULLY ===");
                Console.WriteLine($"Deleted blob: {blobUrl}");

                _logger.LogInformation("Successfully deleted PDF blob: {BlobUrl}", blobUrl);
                _logger.LogInformation("DEBUG - Blob deleted successfully: {BlobUrl}", blobUrl);
            }
            else
            {
                // DEBUG: Log blob not found to browser console (production: remove this section)
                await _debugConsole.LogWarningAsync("BLOB NOT FOUND FOR DELETION");
                await _debugConsole.LogAsync($"Blob not found: {blobUrl}");

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
            await _debugConsole.LogErrorAsync("BLOB DELETE FAILED");
            await _debugConsole.LogErrorAsync($"Error: {ex.Message}");

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
        // For development storage, we need to handle Azurite not being available
        var containerClient = _blobServiceClient.GetBlobContainerClient(_settings.ContainerName);
        
        // Only attempt to create container if not using development storage fallback
        if (_settings.ConnectionString != "UseDevelopmentStorage=true")
        {
            await containerClient.CreateIfNotExistsAsync(PublicAccessType.None);
        }
        else
        {
            // For development storage, try to create but don't fail if Azurite is not running
            try
            {
                await containerClient.CreateIfNotExistsAsync(PublicAccessType.None);
            }
            catch (Exception ex) when (ex.Message.Contains("Connection refused") || ex.Message.Contains("127.0.0.1:10000"))
            {
                // Azurite is not running, this will be handled in the calling method
                throw;
            }
        }
        
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

    /// <summary>
    /// Development fallback storage when Azurite is not available
    /// Saves files to local file system for development testing
    /// </summary>
    private async Task<string> UploadToLocalDevelopmentStorageAsync(byte[] pdfData, string fileName, string submissionId)
    {
        try
        {
            // Create local development storage directory
            var baseDir = Path.Combine(Path.GetTempPath(), "azure-accommodation-form-dev-storage", _settings.ContainerName);
            var submissionDir = Path.Combine(baseDir, submissionId);
            
            Directory.CreateDirectory(submissionDir);
            
            var filePath = Path.Combine(submissionDir, fileName);
            
            // DEBUG: Log local storage details to browser console (production: remove this section)
            await _debugConsole.LogGroupAsync("LOCAL DEVELOPMENT STORAGE");
            await _debugConsole.LogAsync($"Storage Directory: {baseDir}");
            await _debugConsole.LogAsync($"Submission Directory: {submissionDir}");
            await _debugConsole.LogAsync($"File Path: {filePath}");
            await _debugConsole.LogAsync($"File Size: {pdfData.Length} bytes");
            await _debugConsole.LogGroupEndAsync();

            // DEBUG: Log local storage details (production: remove this section)
            Console.WriteLine("=== LOCAL DEVELOPMENT STORAGE ===");
            Console.WriteLine($"Storage Directory: {baseDir}");
            Console.WriteLine($"Submission Directory: {submissionDir}");
            Console.WriteLine($"File Path: {filePath}");
            Console.WriteLine($"File Size: {pdfData.Length} bytes");

            _logger.LogInformation("DEBUG - Local development storage: BaseDir={BaseDir}, FilePath={FilePath}, FileSize={FileSize}",
                baseDir, filePath, pdfData.Length);

            // Write the file to local storage
            await File.WriteAllBytesAsync(filePath, pdfData);

            // Create a local file URL for development
            var localUrl = $"file://{filePath.Replace('\\', '/')}";

            // DEBUG: Log successful local save to browser console (production: remove this section)
            await _debugConsole.LogInfoAsync("LOCAL FILE SAVED SUCCESSFULLY");
            await _debugConsole.LogAsync($"Local URL: {localUrl}");

            // DEBUG: Log successful local save (production: remove this section)
            Console.WriteLine("=== LOCAL FILE SAVED SUCCESSFULLY ===");
            Console.WriteLine($"Local URL: {localUrl}");

            _logger.LogInformation("Successfully saved PDF to local development storage: {FilePath}", filePath);
            _logger.LogInformation("DEBUG - Local file saved successfully: {LocalUrl}", localUrl);

            return localUrl;
        }
        catch (Exception ex)
        {
            // DEBUG: Enhanced error logging to browser console (production: keep but remove DEBUG prefix)
            await _debugConsole.LogErrorAsync("LOCAL STORAGE SAVE FAILED");
            await _debugConsole.LogErrorAsync($"Error: {ex.Message}");

            // DEBUG: Enhanced error logging (production: keep but remove DEBUG prefix)
            Console.WriteLine($"=== LOCAL STORAGE SAVE FAILED ===");
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");

            _logger.LogError(ex, "Failed to save PDF to local development storage for submission {SubmissionId}", submissionId);
            throw;
        }
    }
}