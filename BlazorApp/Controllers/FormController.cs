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
    /// Submit the completed form data
    /// </summary>
    [HttpPost("submit")]
    public async Task<ActionResult<FormSubmissionResponse>> SubmitForm([FromBody] FormSubmissionRequest request)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var result = await _formService.SubmitFormAsync(request.SubmissionId, request.FormData);
        
        if (result.Success)
        {
            return Ok(result);
        }
        
        return BadRequest(result);
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