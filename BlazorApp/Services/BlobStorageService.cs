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
            var containerClient = await GetContainerClientAsync();
            var blobName = $"{submissionId}/{fileName}";
            var blobClient = containerClient.GetBlobClient(blobName);

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

            _logger.LogInformation("Successfully uploaded PDF {FileName} for submission {SubmissionId}", fileName, submissionId);
            
            return blobClient.Uri.ToString();
        }
        catch (Exception ex)
        {
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
}