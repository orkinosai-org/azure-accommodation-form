using Microsoft.AspNetCore.Mvc;
using BlazorApp.Services;
using BlazorApp.Models;
using System.ComponentModel.DataAnnotations;

namespace BlazorApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class FormController : ControllerBase
{
    private readonly IFormService _formService;
    private readonly ILogger<FormController> _logger;

    public FormController(IFormService formService, ILogger<FormController> logger)
    {
        _formService = formService;
        _logger = logger;
    }

    /// <summary>
    /// Initialize a new form submission session
    /// </summary>
    [HttpPost("initialize")]
    public async Task<ActionResult<FormSubmissionResponse>> InitializeForm([FromBody] InitializeFormRequest request)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var result = await _formService.InitializeFormSessionAsync(request.Email);
        
        if (result.Success)
        {
            return Ok(result);
        }
        
        return BadRequest(result);
    }

    /// <summary>
    /// Send email verification token to the user
    /// </summary>
    [HttpPost("send-verification")]
    public async Task<ActionResult<EmailVerificationResponse>> SendEmailVerification([FromBody] EmailVerificationRequest request)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var result = await _formService.SendEmailVerificationAsync(request.SubmissionId, request.Email);
        
        if (result.Success)
        {
            return Ok(result);
        }
        
        return BadRequest(result);
    }

    /// <summary>
    /// Verify email using the token sent to user's email
    /// </summary>
    [HttpPost("verify-email")]
    public async Task<ActionResult<FormSubmissionResponse>> VerifyEmail([FromBody] TokenVerificationRequest request)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var result = await _formService.VerifyEmailTokenAsync(request.SubmissionId, request.Token);
        
        if (result.Success)
        {
            return Ok(result);
        }
        
        return BadRequest(result);
    }

    /// <summary>
    /// Submit form data directly without email verification (for API usage)
    /// </summary>
    [HttpPost("submit-direct")]
    public async Task<ActionResult<FormSubmissionResponse>> SubmitFormDirect([FromBody] FormData formData)
    {
        var requestTimestamp = DateTime.UtcNow;
        var requestId = Guid.NewGuid().ToString("N")[..8]; // Short request ID for tracking
        var isDevelopment = HttpContext.RequestServices.GetService<IWebHostEnvironment>()?.IsDevelopment() == true;
        
        // DEBUG: Enhanced API entry logging for troubleshooting
        _logger.LogInformation("=== FORM CONTROLLER: DIRECT SUBMISSION ENTRY (Request: {RequestId}) ===", requestId);
        _logger.LogInformation("Request received at {Timestamp}", requestTimestamp);
        _logger.LogInformation("Request ID: {RequestId}", requestId);
        _logger.LogInformation("Environment: {Environment}", isDevelopment ? "Development" : "Production");
        _logger.LogInformation("Model State Valid: {IsValid}", ModelState.IsValid);
        _logger.LogInformation("User Email: {Email}", formData?.TenantDetails?.Email);
        _logger.LogInformation("User Name: {Name}", formData?.TenantDetails?.FullName);
        _logger.LogInformation("Request Content-Type: {ContentType}", Request.ContentType);
        _logger.LogInformation("Request Content-Length: {ContentLength}", Request.ContentLength);
        _logger.LogInformation("User-Agent: {UserAgent}", Request.Headers.UserAgent.ToString());
        
        // DEVELOPMENT MODE: Log complete request payload for debugging (never in production)
        if (isDevelopment && formData != null)
        {
            try
            {
                var requestPayloadJson = System.Text.Json.JsonSerializer.Serialize(formData, new System.Text.Json.JsonSerializerOptions 
                { 
                    WriteIndented = true,
                    PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase
                });
                _logger.LogInformation("DEVELOPMENT ONLY - Request Payload (Request: {RequestId}): {RequestPayload}", requestId, requestPayloadJson);
            }
            catch (Exception serializationEx)
            {
                _logger.LogWarning("DEVELOPMENT ONLY - Failed to serialize request payload for logging (Request: {RequestId}): {Error}", requestId, serializationEx.Message);
            }
        }
        
        Console.WriteLine($"=== FORM CONTROLLER: DIRECT SUBMISSION ENTRY (Request: {requestId}) ===");
        Console.WriteLine($"Request received at {requestTimestamp}");
        Console.WriteLine($"Request ID: {requestId}");
        Console.WriteLine($"Model State Valid: {ModelState.IsValid}");
        Console.WriteLine($"User Email: {formData?.TenantDetails?.Email}");
        Console.WriteLine($"User Name: {formData?.TenantDetails?.FullName}");
        Console.WriteLine($"Request Content-Type: {Request.ContentType}");
        Console.WriteLine($"Request Content-Length: {Request.ContentLength}");
        Console.WriteLine($"User-Agent: {Request.Headers.UserAgent}");

        if (!ModelState.IsValid)
        {
            _logger.LogWarning("Model state validation failed for direct form submission (Request: {RequestId})", requestId);
            Console.WriteLine($"=== MODEL STATE VALIDATION FAILED (Request: {requestId}) ===");
            
            var validationErrors = new List<string>();
            var detailedValidationInfo = new List<string>();
            
            foreach (var modelError in ModelState)
            {
                foreach (var error in modelError.Value.Errors)
                {
                    var errorMsg = $"Field: {modelError.Key}, Error: {error.ErrorMessage}";
                    validationErrors.Add(errorMsg);
                    _logger.LogWarning("Model Error - {ErrorMessage}", errorMsg);
                    Console.WriteLine($"Model Error - {errorMsg}");
                    
                    // DEVELOPMENT MODE: Add detailed validation information for debugging
                    if (isDevelopment)
                    {
                        var fieldValue = "Not Available";
                        try
                        {
                            // Try to get the actual field value for debugging
                            if (modelError.Value.AttemptedValue != null)
                            {
                                fieldValue = modelError.Value.AttemptedValue;
                            }
                            else if (formData != null)
                            {
                                // Try to extract the field value from the form data using reflection
                                var fieldPath = modelError.Key.Split('.');
                                object? currentObj = formData;
                                foreach (var segment in fieldPath)
                                {
                                    if (currentObj == null) break;
                                    var property = currentObj.GetType().GetProperty(segment);
                                    if (property != null)
                                    {
                                        currentObj = property.GetValue(currentObj);
                                    }
                                    else
                                    {
                                        currentObj = null;
                                        break;
                                    }
                                }
                                if (currentObj != null)
                                {
                                    fieldValue = currentObj.ToString() ?? "null";
                                }
                            }
                        }
                        catch
                        {
                            fieldValue = "Unable to retrieve";
                        }
                        
                        var detailedInfo = $"Field: {modelError.Key}, Value: '{fieldValue}', Error: {error.ErrorMessage}";
                        detailedValidationInfo.Add(detailedInfo);
                        _logger.LogWarning("DEVELOPMENT ONLY - Detailed validation error: {DetailedError}", detailedInfo);
                    }
                }
            }
            
            // DEVELOPMENT MODE: Log form data structure for validation debugging
            if (isDevelopment && formData != null)
            {
                try
                {
                    var formStructureInfo = new
                    {
                        TenantDetailsProvided = formData.TenantDetails != null,
                        BankDetailsProvided = formData.BankDetails != null,
                        AddressHistoryCount = formData.AddressHistory?.Count ?? 0,
                        ContactsCount = formData.Contacts != null ? 1 : 0,
                        MedicalDetailsProvided = formData.MedicalDetails != null,
                        EmploymentProvided = formData.Employment != null,
                        PassportDetailsProvided = formData.PassportDetails != null,
                        CurrentLivingArrangementProvided = formData.CurrentLivingArrangement != null,
                        OtherProvided = formData.Other != null,
                        ConsentAndDeclarationProvided = formData.ConsentAndDeclaration != null
                    };
                    var structureJson = System.Text.Json.JsonSerializer.Serialize(formStructureInfo, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });
                    _logger.LogInformation("DEVELOPMENT ONLY - Form data structure analysis (Request: {RequestId}): {FormStructure}", requestId, structureJson);
                }
                catch (Exception structureEx)
                {
                    _logger.LogWarning("DEVELOPMENT ONLY - Failed to analyze form structure (Request: {RequestId}): {Error}", requestId, structureEx.Message);
                }
            }
            
            var baseMessage = "Form validation failed. Please check all required fields and try again.";
            var responseMessage = baseMessage;
            
            // In development mode, include detailed validation information
            if (isDevelopment && detailedValidationInfo.Any())
            {
                responseMessage += $" [Dev Validation Details: {string.Join("; ", detailedValidationInfo)}]";
            }
            
            var response = new FormSubmissionResponse
            {
                Success = false,
                Message = responseMessage,
                SubmissionId = "",
                Status = FormSubmissionStatus.Failed,
                Timestamp = DateTime.UtcNow
            };
            
            // Enhanced error response with detailed validation information
            _logger.LogInformation("API Response (Request: {RequestId}): {Response}", requestId, 
                System.Text.Json.JsonSerializer.Serialize(response));
            Console.WriteLine($"API Response (Request: {requestId}): {System.Text.Json.JsonSerializer.Serialize(response)}");
            
            return BadRequest(response);
        }

        // CRITICAL VALIDATION: Check consent is given regardless of ModelState
        if (formData?.ConsentAndDeclaration?.ConsentGiven != true)
        {
            _logger.LogWarning("CONSENT VALIDATION FAILED: User consent not given for submission (Request: {RequestId})", requestId);
            Console.WriteLine($"=== CONSENT VALIDATION FAILED (Request: {requestId}) ===");
            Console.WriteLine($"ConsentGiven value: {formData?.ConsentAndDeclaration?.ConsentGiven}");
            
            var consentResponse = new FormSubmissionResponse
            {
                Success = false,
                Message = "You must consent to the processing of your personal data to submit this form.",
                SubmissionId = "",
                Status = FormSubmissionStatus.Failed,
                Timestamp = DateTime.UtcNow
            };
            
            _logger.LogInformation("Consent validation failed - API Response (Request: {RequestId}): {Response}", requestId, 
                System.Text.Json.JsonSerializer.Serialize(consentResponse));
            Console.WriteLine($"Consent validation failed - API Response (Request: {requestId}): {System.Text.Json.JsonSerializer.Serialize(consentResponse)}");
            
            return BadRequest(consentResponse);
        }

        // CRITICAL VALIDATION: Check required declaration fields
        var declaration = formData?.ConsentAndDeclaration?.Declaration;
        if (declaration != null)
        {
            var declarationErrors = new List<string>();
            
            if (!declaration.MainHome)
                declarationErrors.Add("You must declare this will be your main home.");
            if (!declaration.EnquiriesPermission)
                declarationErrors.Add("You must give permission for enquiries to be made.");
            if (!declaration.CertifyNoJudgements)
                declarationErrors.Add("You must certify no outstanding county court judgements.");
            if (!declaration.CertifyNoHousingDebt)
                declarationErrors.Add("You must certify no housing-related debt.");
            if (!declaration.CertifyNoLandlordDebt)
                declarationErrors.Add("You must certify no debt to previous landlords.");
            if (!declaration.CertifyNoAbuse)
                declarationErrors.Add("You must certify no history of property abuse.");
            
            if (declarationErrors.Any())
            {
                _logger.LogWarning("DECLARATION VALIDATION FAILED: Required declarations not completed (Request: {RequestId})", requestId);
                Console.WriteLine($"=== DECLARATION VALIDATION FAILED (Request: {requestId}) ===");
                foreach (var error in declarationErrors)
                {
                    Console.WriteLine($"Declaration Error: {error}");
                }
                
                var declarationResponse = new FormSubmissionResponse
                {
                    Success = false,
                    Message = $"Please complete all required declarations: {string.Join(" ", declarationErrors)}",
                    SubmissionId = "",
                    Status = FormSubmissionStatus.Failed,
                    Timestamp = DateTime.UtcNow
                };
                
                _logger.LogInformation("Declaration validation failed - API Response (Request: {RequestId}): {Response}", requestId, 
                    System.Text.Json.JsonSerializer.Serialize(declarationResponse));
                Console.WriteLine($"Declaration validation failed - API Response (Request: {requestId}): {System.Text.Json.JsonSerializer.Serialize(declarationResponse)}");
                
                return BadRequest(declarationResponse);
            }
        }

        try
        {
            var requestMetadata = CaptureRequestMetadata();
            
            _logger.LogInformation("Processing direct form submission for {Email} from IP {ClientIp} (Request: {RequestId})", 
                formData.TenantDetails.Email, requestMetadata.IpAddress, requestId);
            Console.WriteLine($"Processing direct form submission for {formData.TenantDetails.Email} from IP {requestMetadata.IpAddress} (Request: {requestId})");
            
            var processingStartTime = DateTime.UtcNow;
            var result = await _formService.ProcessFormDirectAsync(formData, requestMetadata);
            var processingDuration = DateTime.UtcNow - processingStartTime;
            
            // Enhanced response logging with timing information
            _logger.LogInformation("Direct form submission completed - Success: {Success}, Message: {Message}, Duration: {Duration}ms (Request: {RequestId})", 
                result.Success, result.Message, processingDuration.TotalMilliseconds, requestId);
            Console.WriteLine($"Direct form submission completed - Success: {result.Success}, Message: {result.Message}, Duration: {processingDuration.TotalMilliseconds}ms (Request: {requestId})");
            
            // Add request tracking to response
            result.Timestamp = DateTime.UtcNow;
            
            // Log the complete API response for debugging
            var responseJson = System.Text.Json.JsonSerializer.Serialize(result, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });
            _logger.LogInformation("API Response (Request: {RequestId}): {Response}", requestId, responseJson);
            Console.WriteLine($"API Response (Request: {requestId}): {responseJson}");
            
            if (result.Success)
            {
                return Ok(result);
            }
            
            return BadRequest(result);
        }
        catch (Exception ex)
        {
            var processingDuration = DateTime.UtcNow - requestTimestamp;
            
            // Enhanced error logging with complete exception details and stack traces
            _logger.LogError(ex, "Error in direct form submission for {Email} after {Duration}ms (Request: {RequestId})", 
                formData?.TenantDetails?.Email, processingDuration.TotalMilliseconds, requestId);
            
            // DEVELOPMENT MODE: Log comprehensive error details including inner exceptions and full stack trace
            if (isDevelopment)
            {
                _logger.LogError("DEVELOPMENT ONLY - Complete Exception Details (Request: {RequestId}):", requestId);
                _logger.LogError("Exception Type: {ExceptionType}", ex.GetType().FullName);
                _logger.LogError("Exception Message: {ExceptionMessage}", ex.Message);
                _logger.LogError("Exception Source: {ExceptionSource}", ex.Source);
                _logger.LogError("Exception StackTrace: {StackTrace}", ex.StackTrace);
                
                // Log inner exceptions recursively
                var innerEx = ex.InnerException;
                var innerLevel = 1;
                while (innerEx != null)
                {
                    _logger.LogError("Inner Exception Level {Level} - Type: {InnerType}, Message: {InnerMessage}", 
                        innerLevel, innerEx.GetType().FullName, innerEx.Message);
                    _logger.LogError("Inner Exception Level {Level} - StackTrace: {InnerStackTrace}", 
                        innerLevel, innerEx.StackTrace);
                    innerEx = innerEx.InnerException;
                    innerLevel++;
                }
                
                // Log additional exception data if available
                if (ex.Data.Count > 0)
                {
                    _logger.LogError("Exception Data: {ExceptionData}", string.Join(", ", ex.Data.Cast<System.Collections.DictionaryEntry>().Select(de => $"{de.Key}={de.Value}")));
                }
            }
            
            Console.WriteLine($"=== FORM CONTROLLER EXCEPTION (Request: {requestId}) ===");
            Console.WriteLine($"Duration before exception: {processingDuration.TotalMilliseconds}ms");
            Console.WriteLine($"Exception: {ex.GetType().Name}");
            Console.WriteLine($"Message: {ex.Message}");
            
            // Enhanced console logging for development mode
            if (isDevelopment)
            {
                Console.WriteLine($"DEVELOPMENT MODE - Full Exception Details:");
                Console.WriteLine($"Exception Type: {ex.GetType().FullName}");
                Console.WriteLine($"Exception Source: {ex.Source}");
                Console.WriteLine($"Stack Trace: {ex.StackTrace}");
                
                var innerEx = ex.InnerException;
                var innerLevel = 1;
                while (innerEx != null)
                {
                    Console.WriteLine($"Inner Exception Level {innerLevel}: {innerEx.GetType().FullName} - {innerEx.Message}");
                    Console.WriteLine($"Inner Exception Level {innerLevel} StackTrace: {innerEx.StackTrace}");
                    innerEx = innerEx.InnerException;
                    innerLevel++;
                }
            }
            else
            {
                Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            }
            
            // Provide more detailed error messages based on exception type and context
            string userFriendlyMessage;
            string technicalDetails = ex.Message;
            
            // Enhanced error categorization for better root cause analysis
            if (ex is InvalidOperationException && ex.Message.Contains("connection string"))
            {
                userFriendlyMessage = "Configuration error: Storage service is not properly configured for development mode";
                technicalDetails = $"Azure Blob Storage connection string is invalid or Azure Storage Emulator (Azurite) is not running. Details: {ex.Message}";
            }
            else if (ex.Message.Contains("Azure Storage") || ex.Message.Contains("BlobServiceClient") || ex.Message.Contains("blob"))
            {
                userFriendlyMessage = "Storage service is temporarily unavailable. The form data has been validated but could not be permanently stored";
                technicalDetails = $"Azure Blob Storage service error - check connection string and service availability. Error: {ex.Message}";
                
                // Check for specific Azure Storage errors
                if (ex.Message.Contains("Connection refused") || ex.Message.Contains("127.0.0.1:10000"))
                {
                    technicalDetails += " [Azurite not running - start with 'azurite --silent --location c:\\azurite --debug c:\\azurite\\debug.log']";
                }
            }
            else if (ex.Message.Contains("email") || ex.Message.Contains("smtp") || ex.Message.Contains("mail"))
            {
                userFriendlyMessage = "Email service is temporarily unavailable. Your form has been submitted but confirmation emails may not be sent";
                technicalDetails = $"SMTP email service error - check email configuration. Error: {ex.Message}";
            }
            else if (ex.Message.Contains("database") || ex.Message.Contains("DbUpdate") || ex.Message.Contains("SQL") || ex.Message.Contains("Entity"))
            {
                userFriendlyMessage = "Database service is temporarily unavailable. Please try submitting your form again";
                technicalDetails = $"Database connection or update error. Error: {ex.Message}";
            }
            else if (ex.Message.Contains("pdf") || ex.Message.Contains("PDF") || ex.Message.Contains("generation") || ex.Message.Contains("QuestPDF"))
            {
                userFriendlyMessage = "Document generation error occurred";
                technicalDetails = $"Failed to generate PDF document from form data. Error: {ex.Message}";
            }
            else if (ex.Message.Contains("validation") || ex.Message.Contains("required") || ex.Message.Contains("invalid"))
            {
                userFriendlyMessage = "Form data validation failed";
                technicalDetails = $"One or more form fields contain invalid data. Error: {ex.Message}";
            }
            else if (ex is System.IO.DirectoryNotFoundException || ex is System.IO.FileNotFoundException || ex is System.UnauthorizedAccessException)
            {
                userFriendlyMessage = "File system access error occurred";
                technicalDetails = $"Cannot access required directories or files. Check permissions and disk space. Error: {ex.Message}";
            }
            else if (ex is System.Net.Http.HttpRequestException || ex.Message.Contains("network") || ex.Message.Contains("connection"))
            {
                userFriendlyMessage = "Network connectivity issue occurred";
                technicalDetails = $"Failed to connect to external services (email or storage). Error: {ex.Message}";
            }
            else
            {
                userFriendlyMessage = "An unexpected error occurred while processing your submission. Please try again later";
                technicalDetails = ex.Message;
            }
            
            var errorResponse = new FormSubmissionResponse
            {
                Success = false,
                Message = userFriendlyMessage,
                SubmissionId = "",
                Status = FormSubmissionStatus.Failed,
                Timestamp = DateTime.UtcNow
            };
            
            // In development mode, include comprehensive technical details for debugging
            if (isDevelopment)
            {
                var devDetails = $"[Dev Details: {technicalDetails}]";
                if (ex.InnerException != null)
                {
                    devDetails += $" [Inner Exception: {ex.InnerException.GetType().Name}: {ex.InnerException.Message}]";
                }
                devDetails += $" [Stack Trace: {ex.StackTrace}]";
                errorResponse.Message += $" {devDetails}";
            }
            
            // Log error response for debugging
            var errorResponseJson = System.Text.Json.JsonSerializer.Serialize(errorResponse, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });
            _logger.LogInformation("API Error Response (Request: {RequestId}): {Response}", requestId, errorResponseJson);
            Console.WriteLine($"API Error Response (Request: {requestId}): {errorResponseJson}");
            
            return StatusCode(500, errorResponse);
        }
    }

    /// <summary>
    /// Submit the completed form data
    /// </summary>
    [HttpPost("submit")]
    public async Task<ActionResult<FormSubmissionResponse>> SubmitForm([FromBody] FormSubmissionRequest request)
    {
        // DEBUG: Enhanced API entry logging for troubleshooting
        _logger.LogInformation("=== FORM CONTROLLER: STANDARD SUBMISSION ENTRY ===");
        _logger.LogInformation("Request received at {Timestamp}", DateTime.UtcNow);
        _logger.LogInformation("Model State Valid: {IsValid}", ModelState.IsValid);
        _logger.LogInformation("Submission ID: {SubmissionId}", request?.SubmissionId);
        _logger.LogInformation("User Email: {Email}", request?.FormData?.TenantDetails?.Email);
        
        Console.WriteLine("=== FORM CONTROLLER: STANDARD SUBMISSION ENTRY ===");
        Console.WriteLine($"Request received at {DateTime.UtcNow}");
        Console.WriteLine($"Model State Valid: {ModelState.IsValid}");
        Console.WriteLine($"Submission ID: {request?.SubmissionId}");
        Console.WriteLine($"User Email: {request?.FormData?.TenantDetails?.Email}");

        if (!ModelState.IsValid)
        {
            _logger.LogWarning("Model state validation failed for standard form submission");
            Console.WriteLine("=== MODEL STATE VALIDATION FAILED ===");
            
            foreach (var modelError in ModelState)
            {
                foreach (var error in modelError.Value.Errors)
                {
                    _logger.LogWarning("Model Error - Key: {Key}, Error: {Error}", modelError.Key, error.ErrorMessage);
                    Console.WriteLine($"Model Error - Key: {modelError.Key}, Error: {error.ErrorMessage}");
                }
            }
            
            return BadRequest(new FormSubmissionResponse
            {
                Success = false,
                Message = "Form validation failed: " + string.Join("; ", ModelState.Values.SelectMany(v => v.Errors).Select(e => e.ErrorMessage))
            });
        }

        // CRITICAL VALIDATION: Check consent is given for standard submission
        if (request?.FormData?.ConsentAndDeclaration?.ConsentGiven != true)
        {
            _logger.LogWarning("CONSENT VALIDATION FAILED: User consent not given for standard submission");
            Console.WriteLine($"=== CONSENT VALIDATION FAILED (Standard Submission) ===");
            Console.WriteLine($"ConsentGiven value: {request?.FormData?.ConsentAndDeclaration?.ConsentGiven}");
            
            return BadRequest(new FormSubmissionResponse
            {
                Success = false,
                Message = "You must consent to the processing of your personal data to submit this form.",
                SubmissionId = "",
                Status = FormSubmissionStatus.Failed,
                Timestamp = DateTime.UtcNow
            });
        }

        // CRITICAL VALIDATION: Check required declaration fields for standard submission
        var declaration = request?.FormData?.ConsentAndDeclaration?.Declaration;
        if (declaration != null)
        {
            var declarationErrors = new List<string>();
            
            if (!declaration.MainHome)
                declarationErrors.Add("You must declare this will be your main home.");
            if (!declaration.EnquiriesPermission)
                declarationErrors.Add("You must give permission for enquiries to be made.");
            if (!declaration.CertifyNoJudgements)
                declarationErrors.Add("You must certify no outstanding county court judgements.");
            if (!declaration.CertifyNoHousingDebt)
                declarationErrors.Add("You must certify no housing-related debt.");
            if (!declaration.CertifyNoLandlordDebt)
                declarationErrors.Add("You must certify no debt to previous landlords.");
            if (!declaration.CertifyNoAbuse)
                declarationErrors.Add("You must certify no history of property abuse.");
            
            if (declarationErrors.Any())
            {
                _logger.LogWarning("DECLARATION VALIDATION FAILED: Required declarations not completed for standard submission");
                Console.WriteLine($"=== DECLARATION VALIDATION FAILED (Standard Submission) ===");
                foreach (var error in declarationErrors)
                {
                    Console.WriteLine($"Declaration Error: {error}");
                }
                
                return BadRequest(new FormSubmissionResponse
                {
                    Success = false,
                    Message = $"Please complete all required declarations: {string.Join(" ", declarationErrors)}",
                    SubmissionId = "",
                    Status = FormSubmissionStatus.Failed,
                    Timestamp = DateTime.UtcNow
                });
            }
        }

        try
        {
            var requestMetadata = CaptureRequestMetadata();
            
            _logger.LogInformation("Processing standard form submission for {Email} from IP {ClientIp}", 
                request.FormData.TenantDetails.Email, requestMetadata.IpAddress);
            Console.WriteLine($"Processing standard form submission for {request.FormData.TenantDetails.Email} from IP {requestMetadata.IpAddress}");
            
            var result = await _formService.SubmitFormAsync(request.SubmissionId, request.FormData, requestMetadata);
            
            _logger.LogInformation("Standard form submission completed - Success: {Success}, Message: {Message}", 
                result.Success, result.Message);
            Console.WriteLine($"Standard form submission completed - Success: {result.Success}, Message: {result.Message}");
            
            if (result.Success)
            {
                return Ok(result);
            }
            
            return BadRequest(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in standard form submission for {SubmissionId}", request?.SubmissionId);
            Console.WriteLine($"=== FORM CONTROLLER EXCEPTION ===");
            Console.WriteLine($"Exception: {ex.GetType().Name}");
            Console.WriteLine($"Message: {ex.Message}");
            Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            
            return StatusCode(500, new FormSubmissionResponse
            {
                Success = false,
                Message = "An internal error occurred while processing your submission. Please try again."
            });
        }
    }

    /// <summary>
    /// Get submission status and details (for debugging/admin purposes)
    /// </summary>
    [HttpGet("{submissionId}/status")]
    public async Task<ActionResult<FormSubmissionStatusResponse>> GetSubmissionStatus(string submissionId)
    {
        if (string.IsNullOrEmpty(submissionId))
        {
            return BadRequest("Submission ID is required");
        }

        var submission = await _formService.GetSubmissionAsync(submissionId);
        
        if (submission == null)
        {
            return NotFound("Submission not found");
        }

        var response = new FormSubmissionStatusResponse
        {
            SubmissionId = submission.SubmissionId,
            Status = submission.Status,
            UserEmail = submission.UserEmail,
            SubmittedAt = submission.SubmittedAt,
            EmailVerified = submission.EmailVerified,
            PdfFileName = submission.PdfFileName,
            BlobStorageUrl = submission.BlobStorageUrl,
            Logs = submission.Logs.Select(l => new SubmissionLogDto
            {
                Action = l.Action,
                Details = l.Details,
                Timestamp = l.Timestamp
            }).ToList()
        };

        return Ok(response);
    }

    /// <summary>
    /// Get the client IP address from the HTTP context
    /// </summary>
    private string GetClientIpAddress()
    {
        // Check for forwarded IP address first (for load balancers/proxies)
        if (Request.Headers.ContainsKey("X-Forwarded-For"))
        {
            var forwardedIps = Request.Headers["X-Forwarded-For"].ToString().Split(',');
            if (forwardedIps.Length > 0 && !string.IsNullOrWhiteSpace(forwardedIps[0]))
            {
                return forwardedIps[0].Trim();
            }
        }

        // Check for real IP header (some load balancers use this)
        if (Request.Headers.ContainsKey("X-Real-IP"))
        {
            var realIp = Request.Headers["X-Real-IP"].ToString();
            if (!string.IsNullOrWhiteSpace(realIp))
            {
                return realIp.Trim();
            }
        }

        // Fall back to remote IP address
        var remoteIpAddress = HttpContext.Connection.RemoteIpAddress;
        if (remoteIpAddress != null)
        {
            // Handle IPv4 mapped to IPv6
            if (remoteIpAddress.IsIPv4MappedToIPv6)
            {
                return remoteIpAddress.MapToIPv4().ToString();
            }
            return remoteIpAddress.ToString();
        }

        return "Unknown";
    }

    /// <summary>
    /// Capture comprehensive request metadata for audit and compliance purposes
    /// </summary>
    private RequestMetadata CaptureRequestMetadata()
    {
        var metadata = new RequestMetadata
        {
            IpAddress = GetClientIpAddress(),
            UserAgent = Request.Headers.UserAgent.ToString(),
            Referrer = Request.Headers.Referer.ToString(),
            AcceptLanguage = Request.Headers.AcceptLanguage.ToString(),
            Origin = Request.Headers.Origin.ToString(),
            XForwardedFor = Request.Headers.ContainsKey("X-Forwarded-For") ? Request.Headers["X-Forwarded-For"].ToString() : null,
            XRealIp = Request.Headers.ContainsKey("X-Real-IP") ? Request.Headers["X-Real-IP"].ToString() : null,
            ContentType = Request.ContentType,
            ContentLength = Request.ContentLength,
            RequestTimestamp = DateTime.UtcNow,
            Host = Request.Host.ToString(),
            Protocol = Request.Protocol,
            Method = Request.Method,
            Path = Request.Path,
            QueryString = Request.QueryString.ToString()
        };

        // Capture security-relevant headers for audit purposes
        var securityHeaders = new[] 
        {
            "X-Forwarded-Proto",
            "X-Forwarded-Host", 
            "X-Forwarded-Port",
            "X-Original-Host",
            "CF-Connecting-IP", // Cloudflare
            "True-Client-IP",   // Cloudflare
            "CF-RAY",           // Cloudflare request ID
            "X-Amzn-Trace-Id",  // AWS
            "X-Azure-ClientIP", // Azure
            "X-Azure-SocketIP"  // Azure
        };

        foreach (var headerName in securityHeaders)
        {
            if (Request.Headers.ContainsKey(headerName))
            {
                metadata.SecurityHeaders[headerName] = Request.Headers[headerName].ToString();
            }
        }

        return metadata;
    }
}

// Additional DTOs for API requests/responses
public class InitializeFormRequest
{
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;
}

public class FormSubmissionStatusResponse
{
    public string SubmissionId { get; set; } = string.Empty;
    public FormSubmissionStatus Status { get; set; }
    public string UserEmail { get; set; } = string.Empty;
    public DateTime SubmittedAt { get; set; }
    public bool EmailVerified { get; set; }
    public string PdfFileName { get; set; } = string.Empty;
    public string BlobStorageUrl { get; set; } = string.Empty;
    public List<SubmissionLogDto> Logs { get; set; } = new();
}

public class SubmissionLogDto
{
    public string Action { get; set; } = string.Empty;
    public string? Details { get; set; }
    public DateTime Timestamp { get; set; }
}