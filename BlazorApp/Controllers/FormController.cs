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
        // DEBUG: Enhanced API entry logging for troubleshooting
        _logger.LogInformation("=== FORM CONTROLLER: DIRECT SUBMISSION ENTRY ===");
        _logger.LogInformation("Request received at {Timestamp}", DateTime.UtcNow);
        _logger.LogInformation("Model State Valid: {IsValid}", ModelState.IsValid);
        _logger.LogInformation("User Email: {Email}", formData?.TenantDetails?.Email);
        _logger.LogInformation("User Name: {Name}", formData?.TenantDetails?.FullName);
        
        Console.WriteLine("=== FORM CONTROLLER: DIRECT SUBMISSION ENTRY ===");
        Console.WriteLine($"Request received at {DateTime.UtcNow}");
        Console.WriteLine($"Model State Valid: {ModelState.IsValid}");
        Console.WriteLine($"User Email: {formData?.TenantDetails?.Email}");
        Console.WriteLine($"User Name: {formData?.TenantDetails?.FullName}");

        if (!ModelState.IsValid)
        {
            _logger.LogWarning("Model state validation failed for direct form submission");
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

        try
        {
            var clientIp = GetClientIpAddress();
            
            _logger.LogInformation("Processing direct form submission for {Email} from IP {ClientIp}", 
                formData.TenantDetails.Email, clientIp);
            Console.WriteLine($"Processing direct form submission for {formData.TenantDetails.Email} from IP {clientIp}");
            
            var result = await _formService.ProcessFormDirectAsync(formData, clientIp);
            
            _logger.LogInformation("Direct form submission completed - Success: {Success}, Message: {Message}", 
                result.Success, result.Message);
            Console.WriteLine($"Direct form submission completed - Success: {result.Success}, Message: {result.Message}");
            
            if (result.Success)
            {
                return Ok(result);
            }
            
            return BadRequest(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in direct form submission for {Email}", formData?.TenantDetails?.Email);
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

        try
        {
            var clientIp = GetClientIpAddress();
            
            _logger.LogInformation("Processing standard form submission for {Email} from IP {ClientIp}", 
                request.FormData.TenantDetails.Email, clientIp);
            Console.WriteLine($"Processing standard form submission for {request.FormData.TenantDetails.Email} from IP {clientIp}");
            
            var result = await _formService.SubmitFormAsync(request.SubmissionId, request.FormData, clientIp);
            
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