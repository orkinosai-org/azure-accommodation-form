using BlazorApp.Models;
using System.Text;
using System.Text.Json;

namespace BlazorApp.Services;

public interface IFormApiService
{
    Task<FormSubmissionResponse> InitializeFormAsync(string email);
    Task<EmailVerificationResponse> SendEmailVerificationAsync(string submissionId, string email);
    Task<FormSubmissionResponse> VerifyEmailTokenAsync(string submissionId, string token);
    Task<FormSubmissionResponse> SubmitFormAsync(string submissionId, FormData formData);
    Task<FormSubmissionResponse> SubmitFormDirectAsync(FormData formData);
}

public class FormApiService : IFormApiService
{
    private readonly HttpClient _httpClient;
    private readonly JsonSerializerOptions _jsonOptions;
    private readonly ILogger<FormApiService> _logger;

    public FormApiService(HttpClient httpClient, ILogger<FormApiService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        };
    }

    public async Task<FormSubmissionResponse> InitializeFormAsync(string email)
    {
        try
        {
            var request = new { Email = email };
            var json = JsonSerializer.Serialize(request, _jsonOptions);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("api/form/initialize", content);
            var responseJson = await response.Content.ReadAsStringAsync();

            if (response.IsSuccessStatusCode)
            {
                return JsonSerializer.Deserialize<FormSubmissionResponse>(responseJson, _jsonOptions) 
                    ?? new FormSubmissionResponse { Success = false, Message = "Invalid response format" };
            }
            else
            {
                _logger.LogError("Failed to initialize form: {StatusCode} - {Response}", response.StatusCode, responseJson);
                return new FormSubmissionResponse { Success = false, Message = "Failed to initialize form" };
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error initializing form for email {Email}", email);
            return new FormSubmissionResponse { Success = false, Message = "Network error occurred" };
        }
    }

    public async Task<EmailVerificationResponse> SendEmailVerificationAsync(string submissionId, string email)
    {
        try
        {
            var request = new { SubmissionId = submissionId, Email = email };
            var json = JsonSerializer.Serialize(request, _jsonOptions);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("api/form/send-verification", content);
            var responseJson = await response.Content.ReadAsStringAsync();

            if (response.IsSuccessStatusCode)
            {
                return JsonSerializer.Deserialize<EmailVerificationResponse>(responseJson, _jsonOptions) 
                    ?? new EmailVerificationResponse { Success = false, Message = "Invalid response format" };
            }
            else
            {
                _logger.LogError("Failed to send email verification: {StatusCode} - {Response}", response.StatusCode, responseJson);
                return new EmailVerificationResponse { Success = false, Message = "Failed to send verification email" };
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending email verification for submission {SubmissionId}", submissionId);
            return new EmailVerificationResponse { Success = false, Message = "Network error occurred" };
        }
    }

    public async Task<FormSubmissionResponse> VerifyEmailTokenAsync(string submissionId, string token)
    {
        try
        {
            var request = new { SubmissionId = submissionId, Token = token };
            var json = JsonSerializer.Serialize(request, _jsonOptions);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("api/form/verify-email", content);
            var responseJson = await response.Content.ReadAsStringAsync();

            if (response.IsSuccessStatusCode)
            {
                return JsonSerializer.Deserialize<FormSubmissionResponse>(responseJson, _jsonOptions) 
                    ?? new FormSubmissionResponse { Success = false, Message = "Invalid response format" };
            }
            else
            {
                _logger.LogError("Failed to verify email token: {StatusCode} - {Response}", response.StatusCode, responseJson);
                return new FormSubmissionResponse { Success = false, Message = "Failed to verify email token" };
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error verifying email token for submission {SubmissionId}", submissionId);
            return new FormSubmissionResponse { Success = false, Message = "Network error occurred" };
        }
    }

    public async Task<FormSubmissionResponse> SubmitFormAsync(string submissionId, FormData formData)
    {
        try
        {
            // DEBUG: Enhanced API call logging for troubleshooting
            Console.WriteLine("=== FORM API DEBUG: SUBMIT STANDARD ===");
            Console.WriteLine($"API Call Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
            Console.WriteLine($"Submission ID: {submissionId}");
            Console.WriteLine($"User Email: {formData.TenantDetails.Email}");
            Console.WriteLine($"User Name: {formData.TenantDetails.FullName}");
            
            var request = new { SubmissionId = submissionId, FormData = formData };
            var json = JsonSerializer.Serialize(request, _jsonOptions);
            Console.WriteLine($"JSON Payload Length: {json.Length} characters");
            
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            Console.WriteLine("Sending POST request to: api/form/submit");
            var response = await _httpClient.PostAsync("api/form/submit", content);
            var responseJson = await response.Content.ReadAsStringAsync();

            Console.WriteLine($"Response Status: {response.StatusCode}");
            Console.WriteLine($"Response Content: {responseJson}");

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("=== API CALL SUCCESSFUL ===");
                var result = JsonSerializer.Deserialize<FormSubmissionResponse>(responseJson, _jsonOptions) 
                    ?? new FormSubmissionResponse { Success = false, Message = "Invalid response format" };
                Console.WriteLine($"Parsed Response - Success: {result.Success}, Message: {result.Message}");
                return result;
            }
            else
            {
                Console.WriteLine("=== API CALL FAILED ===");
                _logger.LogError("Failed to submit form: {StatusCode} - {Response}", response.StatusCode, responseJson);
                return new FormSubmissionResponse { Success = false, Message = "Failed to submit form" };
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("=== API CALL EXCEPTION ===");
            Console.WriteLine($"Exception Type: {ex.GetType().Name}");
            Console.WriteLine($"Exception Message: {ex.Message}");
            Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            _logger.LogError(ex, "Error submitting form for submission {SubmissionId}", submissionId);
            return new FormSubmissionResponse { Success = false, Message = "Network error occurred" };
        }
    }

    public async Task<FormSubmissionResponse> SubmitFormDirectAsync(FormData formData)
    {
        try
        {
            // DEBUG: Enhanced API call logging for troubleshooting
            Console.WriteLine("=== FORM API DEBUG: SUBMIT DIRECT ===");
            Console.WriteLine($"API Call Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
            Console.WriteLine($"User Email: {formData.TenantDetails.Email}");
            Console.WriteLine($"User Name: {formData.TenantDetails.FullName}");
            Console.WriteLine($"User Phone: {formData.TenantDetails.Telephone}");
            
            var json = JsonSerializer.Serialize(formData, _jsonOptions);
            Console.WriteLine($"JSON Payload Length: {json.Length} characters");
            Console.WriteLine("JSON Sample (first 200 chars): " + (json.Length > 200 ? json.Substring(0, 200) + "..." : json));
            
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            Console.WriteLine("Sending POST request to: api/form/submit-direct");
            var response = await _httpClient.PostAsync("api/form/submit-direct", content);
            var responseJson = await response.Content.ReadAsStringAsync();

            Console.WriteLine($"Response Status: {response.StatusCode}");
            Console.WriteLine($"Response Content: {responseJson}");

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("=== API CALL SUCCESSFUL ===");
                var result = JsonSerializer.Deserialize<FormSubmissionResponse>(responseJson, _jsonOptions) 
                    ?? new FormSubmissionResponse { Success = false, Message = "Invalid response format" };
                Console.WriteLine($"Parsed Response - Success: {result.Success}, Message: {result.Message}");
                return result;
            }
            else
            {
                Console.WriteLine("=== API CALL FAILED ===");
                _logger.LogError("Failed to submit form directly: {StatusCode} - {Response}", response.StatusCode, responseJson);
                return new FormSubmissionResponse { Success = false, Message = "Failed to submit form" };
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("=== API CALL EXCEPTION ===");
            Console.WriteLine($"Exception Type: {ex.GetType().Name}");
            Console.WriteLine($"Exception Message: {ex.Message}");
            Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            _logger.LogError(ex, "Error submitting form directly");
            return new FormSubmissionResponse { Success = false, Message = "Network error occurred" };
        }
    }
}