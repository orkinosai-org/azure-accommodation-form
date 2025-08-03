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
    private readonly bool _isDevelopment;

    public FormApiService(IHttpClientFactory httpClientFactory, ILogger<FormApiService> logger, IWebHostEnvironment webHostEnvironment, IConfiguration configuration)
    {
        _httpClient = httpClientFactory.CreateClient();
        var baseAddress = configuration["ApplicationSettings:ApplicationUrl"] ?? "https://localhost:5001";
        _httpClient.BaseAddress = new Uri(baseAddress);
        _logger = logger;
        _isDevelopment = webHostEnvironment.IsDevelopment();
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
                
                // Try to parse error response for more details
                string errorMessage = "Failed to submit form";
                try
                {
                    if (!string.IsNullOrEmpty(responseJson))
                    {
                        var errorResponse = JsonSerializer.Deserialize<FormSubmissionResponse>(responseJson, _jsonOptions);
                        if (errorResponse != null && !string.IsNullOrEmpty(errorResponse.Message))
                        {
                            errorMessage = errorResponse.Message;
                        }
                    }
                }
                catch
                {
                    // If we can't parse the error response, check for validation errors
                    if (responseJson.Contains("validation errors") || responseJson.Contains("errors"))
                    {
                        errorMessage = "Form validation failed - please check your input data";
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.InternalServerError)
                    {
                        errorMessage = "Server error occurred during form submission";
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                    {
                        errorMessage = "Invalid form data submitted";
                    }
                }
                
                Console.WriteLine($"Status Code: {response.StatusCode}");
                Console.WriteLine($"Error Message: {errorMessage}");
                Console.WriteLine($"Raw Response: {responseJson}");
                
                return new FormSubmissionResponse { Success = false, Message = errorMessage };
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
            var apiCallId = Guid.NewGuid().ToString("N")[..8];
            Console.WriteLine("=== FORM API DEBUG: SUBMIT DIRECT ===");
            Console.WriteLine($"API Call ID: {apiCallId}");
            Console.WriteLine($"API Call Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
            Console.WriteLine($"Environment: {(_isDevelopment ? "Development" : "Production")}");
            Console.WriteLine($"User Email: {formData.TenantDetails.Email}");
            Console.WriteLine($"User Name: {formData.TenantDetails.FullName}");
            Console.WriteLine($"User Phone: {formData.TenantDetails.Telephone}");
            
            var json = JsonSerializer.Serialize(formData, _jsonOptions);
            Console.WriteLine($"JSON Payload Length: {json.Length} characters");
            
            // DEVELOPMENT MODE: Log detailed payload information
            if (_isDevelopment)
            {
                Console.WriteLine("DEVELOPMENT MODE - Additional Debug Info:");
                Console.WriteLine($"Base Address: {_httpClient.BaseAddress}");
                Console.WriteLine($"Timeout: {_httpClient.Timeout}");
                Console.WriteLine($"Default Headers: {string.Join(", ", _httpClient.DefaultRequestHeaders.Select(h => $"{h.Key}: {string.Join(",", h.Value)}"))}");
                Console.WriteLine("JSON Sample (first 300 chars): " + (json.Length > 300 ? json.Substring(0, 300) + "..." : json));
                
                // Log form data completeness for debugging
                var completenessInfo = new
                {
                    TenantDetails = formData.TenantDetails != null,
                    BankDetails = formData.BankDetails != null,
                    AddressHistoryCount = formData.AddressHistory?.Count ?? 0,
                    ContactsCount = formData.Contacts != null ? 1 : 0,
                    SectionsComplete = new[]
                    {
                        formData.TenantDetails != null,
                        formData.BankDetails != null,
                        formData.AddressHistory?.Any() == true,
                        formData.MedicalDetails != null,
                        formData.Employment != null,
                        formData.PassportDetails != null,
                        formData.CurrentLivingArrangement != null,
                        formData.Other != null,
                        formData.ConsentAndDeclaration != null
                    }.Count(x => x)
                };
                Console.WriteLine($"Form Completeness: {JsonSerializer.Serialize(completenessInfo, _jsonOptions)}");
            }
            else
            {
                Console.WriteLine("JSON Sample (first 200 chars): " + (json.Length > 200 ? json.Substring(0, 200) + "..." : json));
            }
            
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            Console.WriteLine("Sending POST request to: api/form/submit-direct");
            var requestStartTime = DateTime.UtcNow;
            var response = await _httpClient.PostAsync("api/form/submit-direct", content);
            var requestDuration = DateTime.UtcNow - requestStartTime;
            var responseJson = await response.Content.ReadAsStringAsync();

            Console.WriteLine($"Response Status: {response.StatusCode} ({(int)response.StatusCode})");
            Console.WriteLine($"Request Duration: {requestDuration.TotalMilliseconds}ms");
            Console.WriteLine($"Response Content: {responseJson}");
            
            // DEVELOPMENT MODE: Log additional response details for debugging
            if (_isDevelopment)
            {
                Console.WriteLine("DEVELOPMENT MODE - Response Debug Details:");
                Console.WriteLine($"Response Headers: {string.Join(", ", response.Headers.Select(h => $"{h.Key}: {string.Join(",", h.Value)}"))}");
                Console.WriteLine($"Content Headers: {string.Join(", ", response.Content.Headers.Select(h => $"{h.Key}: {string.Join(",", h.Value)}"))}");
                Console.WriteLine($"Response Length: {responseJson.Length} characters");
                Console.WriteLine($"Success Status Code: {response.IsSuccessStatusCode}");
                Console.WriteLine($"Reason Phrase: {response.ReasonPhrase}");
                Console.WriteLine($"Response Version: {response.Version}");
            }

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("=== API CALL SUCCESSFUL ===");
                var result = JsonSerializer.Deserialize<FormSubmissionResponse>(responseJson, _jsonOptions) 
                    ?? new FormSubmissionResponse { Success = false, Message = "Invalid response format" };
                Console.WriteLine($"Parsed Response - Success: {result.Success}, Message: {result.Message}");
                
                if (_isDevelopment)
                {
                    Console.WriteLine($"DEVELOPMENT MODE - Complete Response Object: {JsonSerializer.Serialize(result, _jsonOptions)}");
                }
                
                return result;
            }
            else
            {
                Console.WriteLine("=== API CALL FAILED ===");
                _logger.LogError("Failed to submit form directly: {StatusCode} - {Response}", response.StatusCode, responseJson);
                
                // Enhanced error response parsing with development mode details
                string errorMessage = "Failed to submit form";
                string devDetails = "";
                
                try
                {
                    if (!string.IsNullOrEmpty(responseJson))
                    {
                        var errorResponse = JsonSerializer.Deserialize<FormSubmissionResponse>(responseJson, _jsonOptions);
                        if (errorResponse != null && !string.IsNullOrEmpty(errorResponse.Message))
                        {
                            errorMessage = errorResponse.Message;
                            
                            // Extract development details if present
                            if (_isDevelopment && errorMessage.Contains("[Dev Details:"))
                            {
                                var devStart = errorMessage.IndexOf("[Dev Details:");
                                if (devStart >= 0)
                                {
                                    devDetails = errorMessage.Substring(devStart);
                                    errorMessage = errorMessage.Substring(0, devStart).Trim();
                                }
                            }
                        }
                    }
                }
                catch (Exception parseEx)
                {
                    // Enhanced error categorization for better debugging
                    if (responseJson.Contains("validation errors") || responseJson.Contains("errors") || responseJson.Contains("ModelState"))
                    {
                        errorMessage = "Form validation failed - please check your input data";
                        if (_isDevelopment)
                        {
                            devDetails = $"[Dev: Raw validation response: {responseJson}]";
                        }
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.InternalServerError)
                    {
                        errorMessage = "Server error occurred during form submission";
                        if (_isDevelopment)
                        {
                            devDetails = $"[Dev: Parse error: {parseEx.Message}, Raw response: {responseJson}]";
                        }
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                    {
                        errorMessage = "Invalid form data submitted";
                        if (_isDevelopment)
                        {
                            devDetails = $"[Dev: BadRequest details: {responseJson}]";
                        }
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
                    {
                        errorMessage = "Authentication required";
                        if (_isDevelopment)
                        {
                            devDetails = $"[Dev: Auth issue: {responseJson}]";
                        }
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.ServiceUnavailable)
                    {
                        errorMessage = "Service temporarily unavailable";
                        if (_isDevelopment)
                        {
                            devDetails = $"[Dev: Service unavailable: {responseJson}]";
                        }
                    }
                    
                    if (_isDevelopment)
                    {
                        Console.WriteLine($"DEVELOPMENT MODE - Error response parsing failed: {parseEx.Message}");
                    }
                }
                
                Console.WriteLine($"Status Code: {response.StatusCode}");
                Console.WriteLine($"Error Message: {errorMessage}");
                Console.WriteLine($"Raw Response: {responseJson}");
                
                if (_isDevelopment && !string.IsNullOrEmpty(devDetails))
                {
                    Console.WriteLine($"Development Details: {devDetails}");
                    errorMessage += $" {devDetails}";
                }
                
                return new FormSubmissionResponse { Success = false, Message = errorMessage };
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("=== API CALL EXCEPTION ===");
            Console.WriteLine($"Exception Type: {ex.GetType().Name}");
            Console.WriteLine($"Exception Message: {ex.Message}");
            
            // DEVELOPMENT MODE: Enhanced exception logging for debugging
            if (_isDevelopment)
            {
                Console.WriteLine("DEVELOPMENT MODE - Exception Debug Details:");
                Console.WriteLine($"Exception Full Type: {ex.GetType().FullName}");
                Console.WriteLine($"Exception Source: {ex.Source}");
                Console.WriteLine($"Stack Trace: {ex.StackTrace}");
                
                var innerEx = ex.InnerException;
                var level = 1;
                while (innerEx != null)
                {
                    Console.WriteLine($"Inner Exception Level {level}: {innerEx.GetType().FullName} - {innerEx.Message}");
                    innerEx = innerEx.InnerException;
                    level++;
                }
                
                // Log specific HTTP-related details
                if (ex is HttpRequestException httpEx)
                {
                    Console.WriteLine($"HTTP Exception Details: {httpEx.Data}");
                }
                else if (ex is TaskCanceledException taskEx)
                {
                    Console.WriteLine($"Task Cancellation - Timeout: {taskEx.CancellationToken.IsCancellationRequested}");
                }
            }
            else
            {
                Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            }
            
            _logger.LogError(ex, "Error submitting form directly");
            
            var errorMessage = "Network error occurred";
            if (_isDevelopment)
            {
                errorMessage += $" [Dev: {ex.GetType().Name}: {ex.Message}]";
            }
            
            return new FormSubmissionResponse { Success = false, Message = errorMessage };
        }
    }
}