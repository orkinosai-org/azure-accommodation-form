using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace BlazorApp.Models;

// Entity models for database persistence
[Table("FormSubmissions")]
public class FormSubmissionEntity
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public string SubmissionId { get; set; } = Guid.NewGuid().ToString();
    
    [Required]
    public string FormDataJson { get; set; } = string.Empty;
    
    public DateTime SubmittedAt { get; set; } = DateTime.UtcNow;
    
    [MaxLength(320)] // RFC 5321 standard
    public string UserEmail { get; set; } = string.Empty;
    
    public string PdfFileName { get; set; } = string.Empty;
    
    public string BlobStorageUrl { get; set; } = string.Empty;
    
    public string ClientIpAddress { get; set; } = string.Empty;
    
    public FormSubmissionStatus Status { get; set; } = FormSubmissionStatus.Draft;
    
    // Email verification tracking
    public bool EmailVerified { get; set; } = false;
    public string? EmailVerificationToken { get; set; }
    public DateTime? EmailVerificationSent { get; set; }
    public DateTime? EmailVerificationExpires { get; set; }
    
    // Navigation properties
    public virtual ICollection<FormSubmissionLog> Logs { get; set; } = new List<FormSubmissionLog>();
}

[Table("FormSubmissionLogs")]
public class FormSubmissionLog
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public int FormSubmissionId { get; set; }
    
    [Required]
    public string Action { get; set; } = string.Empty;
    
    public string? Details { get; set; }
    
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    
    // Navigation property
    [ForeignKey("FormSubmissionId")]
    public virtual FormSubmissionEntity FormSubmission { get; set; } = null!;
}

public enum FormSubmissionStatus
{
    Draft = 0,
    EmailSent = 1,
    EmailVerified = 2,
    Submitted = 3,
    PdfGenerated = 4,
    Completed = 5,
    Failed = 6
}

// Response DTOs for API
public class FormSubmissionResponse
{
    public string SubmissionId { get; set; } = string.Empty;
    public FormSubmissionStatus Status { get; set; }
    public string Message { get; set; } = string.Empty;
    public bool Success { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class EmailVerificationRequest
{
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;
    
    [Required]
    public string SubmissionId { get; set; } = string.Empty;
}

public class EmailVerificationResponse
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public DateTime TokenExpires { get; set; }
}

public class TokenVerificationRequest
{
    [Required]
    public string SubmissionId { get; set; } = string.Empty;
    
    [Required]
    [StringLength(6, MinimumLength = 5)]
    public string Token { get; set; } = string.Empty;
}

public class FormSubmissionRequest
{
    [Required]
    public string SubmissionId { get; set; } = string.Empty;
    
    [Required]
    public FormData FormData { get; set; } = new();
}