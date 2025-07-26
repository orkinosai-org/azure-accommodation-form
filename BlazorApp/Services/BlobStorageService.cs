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

    public BlobStorageService(
        IOptions<BlobStorageSettings> settings,
        ILogger<BlobStorageService> logger)
    {
        _settings = settings.Value;
        _logger = logger;
        _blobServiceClient = new BlobServiceClient(_settings.ConnectionString);
    }

    public async Task<string> UploadFormPdfAsync(byte[] pdfData, string fileName, string submissionId)
    {
        try
        {
            // DEBUG: Log blob storage configuration (production: remove this section)
            Console.WriteLine("=== BLOB STORAGE DEBUG INFO ===");
            Console.WriteLine($"Container Name: {_settings.ContainerName}");
            
            // Mask connection string secrets
            var maskedConnectionString = MaskConnectionString(_settings.ConnectionString);
            Console.WriteLine($"Connection String: {maskedConnectionString}");

            _logger.LogInformation("DEBUG - Blob storage configuration: Container={ContainerName}, ConnectionString={MaskedConnectionString}",
                _settings.ContainerName, maskedConnectionString);

            var containerClient = await GetContainerClientAsync();
            var blobName = $"{submissionId}/{fileName}";
            var blobClient = containerClient.GetBlobClient(blobName);

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

            // DEBUG: Log successful upload (production: remove this section)
            Console.WriteLine("=== BLOB UPLOADED SUCCESSFULLY ===");
            Console.WriteLine($"Blob URL: {blobClient.Uri}");

            _logger.LogInformation("Successfully uploaded PDF {FileName} for submission {SubmissionId}", fileName, submissionId);
            _logger.LogInformation("DEBUG - Blob uploaded successfully to: {BlobUrl}", blobClient.Uri);
            
            return blobClient.Uri.ToString();
        }
        catch (Exception ex)
        {
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
            
            var containerClient = await GetContainerClientAsync();
            var blobClient = containerClient.GetBlobClient(blobName);

            var response = await blobClient.DeleteIfExistsAsync();
            
            if (response.Value)
            {
                _logger.LogInformation("Successfully deleted PDF blob: {BlobUrl}", blobUrl);
            }
            else
            {
                _logger.LogWarning("Blob not found for deletion: {BlobUrl}", blobUrl);
            }
            
            return response.Value;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete PDF blob: {BlobUrl}", blobUrl);
            return false;
        }
    }

    private async Task<BlobContainerClient> GetContainerClientAsync()
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(_settings.ContainerName);
        await containerClient.CreateIfNotExistsAsync(PublicAccessType.None);
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