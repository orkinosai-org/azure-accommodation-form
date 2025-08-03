using BlazorApp.Data;
using BlazorApp.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using System.Text.Json;

namespace BlazorApp.Services;

public interface IFormService
{
    Task<FormSubmissionResponse> InitializeFormSessionAsync(string email);
    Task<EmailVerificationResponse> SendEmailVerificationAsync(string submissionId, string email);
    Task<FormSubmissionResponse> VerifyEmailTokenAsync(string submissionId, string token);
    Task<FormSubmissionResponse> SubmitFormAsync(string submissionId, FormData formData, string clientIpAddress);
    Task<FormSubmissionResponse> ProcessFormDirectAsync(FormData formData, string clientIpAddress);
    Task<FormSubmissionEntity?> GetSubmissionAsync(string submissionId);
}

public class FormService : IFormService
{
    private readonly ApplicationDbContext _context;
    private readonly IEmailService _emailService;
    private readonly IPdfGenerationService _pdfService;
    private readonly IBlobStorageService _blobService;
    private readonly ApplicationSettings _appSettings;
    private readonly ILogger<FormService> _logger;
    private readonly IDebugConsoleHelper _debugConsole;

    public FormService(
        ApplicationDbContext context,
        IEmailService emailService,
        IPdfGenerationService pdfService,
        IBlobStorageService blobService,
        IOptions<ApplicationSettings> appSettings,
        ILogger<FormService> logger,
        IDebugConsoleHelper debugConsole)
    {
        _context = context;
        _emailService = emailService;
        _pdfService = pdfService;
        _blobService = blobService;
        _appSettings = appSettings.Value;
        _logger = logger;
        _debugConsole = debugConsole;
    }

    public async Task<FormSubmissionResponse> InitializeFormSessionAsync(string email)
    {
        try
        {
            var submissionId = Guid.NewGuid().ToString();
            
            var submission = new FormSubmissionEntity
            {
                SubmissionId = submissionId,
                UserEmail = email,
                FormDataJson = "{}",
                Status = FormSubmissionStatus.Draft
            };

            // FIXED: Create the log entry and add it to the submission's navigation property
            // This way, EF will handle the foreign key relationship correctly
            var log = new FormSubmissionLog
            {
                Action = "SessionInitialized",
                Details = $"Form session initialized for email: {email}",
                Timestamp = DateTime.UtcNow
            };
            
            submission.Logs.Add(log);
            _context.FormSubmissions.Add(submission);
            
            // Save both submission and log in a single transaction
            await _context.SaveChangesAsync();

            _logger.LogInformation("Form session initialized for {Email} with submission ID {SubmissionId}", email, submissionId);

            return new FormSubmissionResponse
            {
                SubmissionId = submissionId,
                Status = FormSubmissionStatus.Draft,
                Message = "Form session initialized successfully",
                Success = true
            };
        }
        catch (Exception ex)
        {
            // Enhanced exception handling with specific DbUpdateException diagnostics
            var errorMessage = "Failed to initialize form session";
            var errorDetails = ex.Message;
            
            // Specific handling for database constraint issues
            if (ex is DbUpdateException dbEx)
            {
                if (dbEx.InnerException?.Message?.Contains("FOREIGN KEY constraint failed") == true)
                {
                    errorMessage = "Database foreign key constraint error during session initialization";
                    errorDetails = "Foreign key constraint failure - data integrity issue detected";
                    _logger.LogError(dbEx, "FOREIGN KEY constraint failed during form session initialization for email {Email}. SQLite Error 19 detected. Inner exception: {InnerExceptionMessage}", 
                        email, dbEx.InnerException?.Message);
                }
                else if (dbEx.InnerException?.Message?.Contains("UNIQUE constraint failed") == true)
                {
                    errorMessage = "Database unique constraint error during session initialization";
                    errorDetails = "Unique constraint failure - duplicate data detected";
                    _logger.LogError(dbEx, "UNIQUE constraint failed during form session initialization for email {Email}. Inner exception: {InnerExceptionMessage}", 
                        email, dbEx.InnerException?.Message);
                }
                else
                {
                    errorMessage = "Database error during session initialization";
                    errorDetails = dbEx.InnerException?.Message ?? dbEx.Message;
                    _logger.LogError(dbEx, "DbUpdateException during form session initialization for email {Email}. Inner exception: {InnerExceptionMessage}", 
                        email, dbEx.InnerException?.Message);
                }
            }
            else
            {
                // Log complete exception details including stack trace for troubleshooting
                _logger.LogError(ex, "Failed to initialize form session for email {Email}. Exception type: {ExceptionType}, Message: {ExceptionMessage}, StackTrace: {StackTrace}", 
                    email, ex.GetType().Name, ex.Message, ex.StackTrace);
                
                // Log inner exceptions if present
                if (ex.InnerException != null)
                {
                    _logger.LogError("Inner exception: {InnerExceptionType}: {InnerExceptionMessage}", 
                        ex.InnerException.GetType().Name, ex.InnerException.Message);
                }
            }
            
            return new FormSubmissionResponse
            {
                Message = errorMessage,
                Success = false
            };
        }
    }

    public async Task<EmailVerificationResponse> SendEmailVerificationAsync(string submissionId, string email)
    {
        try
        {
            var submission = await _context.FormSubmissions
                .FirstOrDefaultAsync(s => s.SubmissionId == submissionId);

            if (submission == null)
            {
                return new EmailVerificationResponse
                {
                    Success = false,
                    Message = "Submission not found"
                };
            }

            // Generate verification token
            var token = GenerateVerificationToken();
            var expiresAt = DateTime.UtcNow.AddMinutes(_appSettings.TokenExpirationMinutes);

            submission.EmailVerificationToken = token;
            submission.EmailVerificationSent = DateTime.UtcNow;
            submission.EmailVerificationExpires = expiresAt;
            submission.UserEmail = email;

            LogSubmissionAction(submission.Id, "EmailVerificationSent", $"Verification token sent to {email}");
            await _context.SaveChangesAsync();

            var emailSent = await _emailService.SendEmailVerificationTokenAsync(email, token, submissionId);

            if (emailSent)
            {
                _logger.LogInformation("Email verification token sent to {Email} for submission {SubmissionId}", email, submissionId);
                return new EmailVerificationResponse
                {
                    Success = true,
                    Message = "Verification email sent successfully",
                    TokenExpires = expiresAt
                };
            }
            else
            {
                LogSubmissionAction(submission.Id, "EmailVerificationFailed", "Failed to send verification email");
                return new EmailVerificationResponse
                {
                    Success = false,
                    Message = "Failed to send verification email"
                };
            }
        }
        catch (Exception ex)
        {
            // Enhanced exception handling with specific DbUpdateException diagnostics
            var errorMessage = "Failed to send email verification";
            var errorDetails = ex.Message;
            
            // Specific handling for database constraint issues
            if (ex is DbUpdateException dbEx)
            {
                if (dbEx.InnerException?.Message?.Contains("FOREIGN KEY constraint failed") == true)
                {
                    errorMessage = "Database foreign key constraint error during email verification";
                    errorDetails = "Foreign key constraint failure - data integrity issue detected";
                    _logger.LogError(dbEx, "FOREIGN KEY constraint failed during email verification for submission {SubmissionId}, email {Email}. SQLite Error 19 detected. Inner exception: {InnerExceptionMessage}", 
                        submissionId, email, dbEx.InnerException?.Message);
                }
                else if (dbEx.InnerException?.Message?.Contains("UNIQUE constraint failed") == true)
                {
                    errorMessage = "Database unique constraint error during email verification";
                    errorDetails = "Unique constraint failure - duplicate data detected";
                    _logger.LogError(dbEx, "UNIQUE constraint failed during email verification for submission {SubmissionId}, email {Email}. Inner exception: {InnerExceptionMessage}", 
                        submissionId, email, dbEx.InnerException?.Message);
                }
                else
                {
                    errorMessage = "Database error during email verification";
                    errorDetails = dbEx.InnerException?.Message ?? dbEx.Message;
                    _logger.LogError(dbEx, "DbUpdateException during email verification for submission {SubmissionId}, email {Email}. Inner exception: {InnerExceptionMessage}", 
                        submissionId, email, dbEx.InnerException?.Message);
                }
            }
            else
            {
                // Log complete exception details including stack trace for troubleshooting
                _logger.LogError(ex, "Failed to send email verification for submission {SubmissionId}, email {Email}. Exception type: {ExceptionType}, Message: {ExceptionMessage}, StackTrace: {StackTrace}", 
                    submissionId, email, ex.GetType().Name, ex.Message, ex.StackTrace);
                
                // Log inner exceptions if present
                if (ex.InnerException != null)
                {
                    _logger.LogError("Inner exception during email verification: {InnerExceptionType}: {InnerExceptionMessage}", 
                        ex.InnerException.GetType().Name, ex.InnerException.Message);
                }
            }
            
            return new EmailVerificationResponse
            {
                Success = false,
                Message = errorMessage
            };
        }
    }

    public async Task<FormSubmissionResponse> VerifyEmailTokenAsync(string submissionId, string token)
    {
        try
        {
            var submission = await _context.FormSubmissions
                .FirstOrDefaultAsync(s => s.SubmissionId == submissionId);

            if (submission == null)
            {
                return new FormSubmissionResponse
                {
                    Message = "Submission not found",
                    Success = false
                };
            }

            if (submission.EmailVerificationToken != token)
            {
                LogSubmissionAction(submission.Id, "EmailVerificationFailed", "Invalid token provided");
                return new FormSubmissionResponse
                {
                    Message = "Invalid verification token",
                    Success = false
                };
            }

            if (submission.EmailVerificationExpires < DateTime.UtcNow)
            {
                LogSubmissionAction(submission.Id, "EmailVerificationFailed", "Token expired");
                return new FormSubmissionResponse
                {
                    Message = "Verification token has expired",
                    Success = false
                };
            }

            submission.EmailVerified = true;
            submission.Status = FormSubmissionStatus.EmailVerified;
            submission.EmailVerificationToken = null; // Clear the token

            LogSubmissionAction(submission.Id, "EmailVerified", "Email successfully verified");
            await _context.SaveChangesAsync();

            _logger.LogInformation("Email verified for submission {SubmissionId}", submissionId);

            return new FormSubmissionResponse
            {
                SubmissionId = submissionId,
                Status = FormSubmissionStatus.EmailVerified,
                Message = "Email verified successfully",
                Success = true
            };
        }
        catch (Exception ex)
        {
            // Enhanced exception handling with specific DbUpdateException diagnostics
            var errorMessage = "Failed to verify email token";
            var errorDetails = ex.Message;
            
            // Specific handling for database constraint issues
            if (ex is DbUpdateException dbEx)
            {
                if (dbEx.InnerException?.Message?.Contains("FOREIGN KEY constraint failed") == true)
                {
                    errorMessage = "Database foreign key constraint error during email token verification";
                    errorDetails = "Foreign key constraint failure - data integrity issue detected";
                    _logger.LogError(dbEx, "FOREIGN KEY constraint failed during email token verification for submission {SubmissionId}. SQLite Error 19 detected. Inner exception: {InnerExceptionMessage}", 
                        submissionId, dbEx.InnerException?.Message);
                }
                else if (dbEx.InnerException?.Message?.Contains("UNIQUE constraint failed") == true)
                {
                    errorMessage = "Database unique constraint error during email token verification";
                    errorDetails = "Unique constraint failure - duplicate data detected";
                    _logger.LogError(dbEx, "UNIQUE constraint failed during email token verification for submission {SubmissionId}. Inner exception: {InnerExceptionMessage}", 
                        submissionId, dbEx.InnerException?.Message);
                }
                else
                {
                    errorMessage = "Database error during email token verification";
                    errorDetails = dbEx.InnerException?.Message ?? dbEx.Message;
                    _logger.LogError(dbEx, "DbUpdateException during email token verification for submission {SubmissionId}. Inner exception: {InnerExceptionMessage}", 
                        submissionId, dbEx.InnerException?.Message);
                }
            }
            else
            {
                // Log complete exception details including stack trace for troubleshooting
                _logger.LogError(ex, "Failed to verify email token for submission {SubmissionId}. Exception type: {ExceptionType}, Message: {ExceptionMessage}, StackTrace: {StackTrace}", 
                    submissionId, ex.GetType().Name, ex.Message, ex.StackTrace);
                
                // Log inner exceptions if present
                if (ex.InnerException != null)
                {
                    _logger.LogError("Inner exception during email token verification: {InnerExceptionType}: {InnerExceptionMessage}", 
                        ex.InnerException.GetType().Name, ex.InnerException.Message);
                }
            }
            
            return new FormSubmissionResponse
            {
                Message = errorMessage,
                Success = false
            };
        }
    }

    public async Task<FormSubmissionResponse> SubmitFormAsync(string submissionId, FormData formData, string clientIpAddress)
    {
        try
        {
            var submission = await _context.FormSubmissions
                .FirstOrDefaultAsync(s => s.SubmissionId == submissionId);

            if (submission == null)
            {
                return new FormSubmissionResponse
                {
                    Message = "Submission not found",
                    Success = false
                };
            }

            if (!submission.EmailVerified)
            {
                return new FormSubmissionResponse
                {
                    Message = "Email must be verified before form submission",
                    Success = false
                };
            }

            // Store form data and client IP
            submission.FormDataJson = JsonSerializer.Serialize(formData, new JsonSerializerOptions { WriteIndented = true });
            submission.ClientIpAddress = clientIpAddress;
            submission.Status = FormSubmissionStatus.Submitted;
            submission.SubmittedAt = DateTime.UtcNow;

            LogSubmissionAction(submission.Id, "FormSubmitted", $"Form data submitted successfully from IP: {clientIpAddress}");

            // Generate PDF with audit trail information
            // DEBUG: Enhanced PDF generation logging to browser console (production: remove DEBUG prefix)
            await _debugConsole.LogInfoAsync("FORM SUBMISSION: PDF GENERATION");
            await _debugConsole.LogAsync($"Starting PDF generation for submission {submissionId}");
            
            Console.WriteLine("=== FORM SUBMISSION: PDF GENERATION ===");
            Console.WriteLine($"Starting PDF generation for submission {submissionId}");
            _logger.LogInformation("DEBUG - Starting PDF generation for submission {SubmissionId}", submissionId);
            
            var pdfData = await _pdfService.GenerateFormPdfAsync(formData, submissionId, submission.SubmittedAt, clientIpAddress);
            var fileName = _pdfService.GenerateFileName(formData, submission.SubmittedAt);
            
            submission.PdfFileName = fileName;
            submission.Status = FormSubmissionStatus.PdfGenerated;

            LogSubmissionAction(submission.Id, "PdfGenerated", $"PDF generated: {fileName}");

            // Upload to blob storage
            // DEBUG: Enhanced blob upload logging to browser console (production: remove DEBUG prefix)
            await _debugConsole.LogInfoAsync("FORM SUBMISSION: BLOB UPLOAD");
            await _debugConsole.LogAsync($"Starting blob upload for submission {submissionId}, file: {fileName}");
            
            Console.WriteLine("=== FORM SUBMISSION: BLOB UPLOAD ===");
            Console.WriteLine($"Starting blob upload for submission {submissionId}, file: {fileName}");
            _logger.LogInformation("DEBUG - Starting blob upload for submission {SubmissionId}, file {FileName}", submissionId, fileName);
            
            var blobUrl = await _blobService.UploadFormPdfAsync(pdfData, fileName, submissionId);
            submission.BlobStorageUrl = blobUrl;

            LogSubmissionAction(submission.Id, "PdfUploaded", $"PDF uploaded to: {blobUrl}");

            // Send confirmation emails
            // DEBUG: Enhanced email sending logging to browser console (production: remove DEBUG prefix)
            await _debugConsole.LogInfoAsync("FORM SUBMISSION: EMAIL SENDING");
            await _debugConsole.LogAsync($"Starting email send for submission {submissionId} to user: {submission.UserEmail}");
            
            Console.WriteLine("=== FORM SUBMISSION: EMAIL SENDING ===");
            Console.WriteLine($"Starting email send for submission {submissionId} to user: {submission.UserEmail}");
            _logger.LogInformation("DEBUG - Starting email send for submission {SubmissionId} to user {UserEmail}", submissionId, submission.UserEmail);
            
            var userEmailSent = await _emailService.SendFormSubmissionConfirmationAsync(
                submission.UserEmail, submissionId, pdfData, fileName);

            await _debugConsole.LogAsync($"Sending company notification email for submission {submissionId}");
            Console.WriteLine($"Sending company notification email for submission {submissionId}");
            var companyEmailSent = await _emailService.SendFormSubmissionToCompanyAsync(
                submissionId, pdfData, fileName, submission.UserEmail);

            if (userEmailSent && companyEmailSent)
            {
                submission.Status = FormSubmissionStatus.Completed;
                LogSubmissionAction(submission.Id, "EmailsSent", "Confirmation emails sent successfully");
            }
            else
            {
                LogSubmissionAction(submission.Id, "EmailSendFailed", 
                    $"Email send status - User: {userEmailSent}, Company: {companyEmailSent}");
            }

            await _context.SaveChangesAsync();

            _logger.LogInformation("Form submission completed successfully for submission {SubmissionId}", submissionId);

            return new FormSubmissionResponse
            {
                SubmissionId = submissionId,
                Status = submission.Status,
                Message = "Form submitted successfully",
                Success = true
            };
        }
        catch (Exception ex)
        {
            // Enhanced exception handling with specific DbUpdateException diagnostics
            var errorMessage = "Failed to submit form";
            var errorDetails = ex.Message;
            
            // Specific handling for database constraint issues
            if (ex is DbUpdateException dbEx)
            {
                if (dbEx.InnerException?.Message?.Contains("FOREIGN KEY constraint failed") == true)
                {
                    errorMessage = "Database foreign key constraint error during form submission";
                    errorDetails = "Foreign key constraint failure - data integrity issue detected";
                    _logger.LogError(dbEx, "FOREIGN KEY constraint failed during form submission for submission {SubmissionId}. SQLite Error 19 detected. Inner exception: {InnerExceptionMessage}", 
                        submissionId, dbEx.InnerException?.Message);
                }
                else if (dbEx.InnerException?.Message?.Contains("UNIQUE constraint failed") == true)
                {
                    errorMessage = "Database unique constraint error during form submission";
                    errorDetails = "Unique constraint failure - duplicate data detected";
                    _logger.LogError(dbEx, "UNIQUE constraint failed during form submission for submission {SubmissionId}. Inner exception: {InnerExceptionMessage}", 
                        submissionId, dbEx.InnerException?.Message);
                }
                else
                {
                    errorMessage = "Database error during form submission";
                    errorDetails = dbEx.InnerException?.Message ?? dbEx.Message;
                    _logger.LogError(dbEx, "DbUpdateException during form submission for submission {SubmissionId}. Inner exception: {InnerExceptionMessage}", 
                        submissionId, dbEx.InnerException?.Message);
                }
            }
            else
            {
                // Log complete exception details including stack trace for troubleshooting
                _logger.LogError(ex, "Failed to submit form for submission {SubmissionId}. Exception type: {ExceptionType}, Message: {ExceptionMessage}, StackTrace: {StackTrace}", 
                    submissionId, ex.GetType().Name, ex.Message, ex.StackTrace);
                
                // Log inner exceptions if present
                if (ex.InnerException != null)
                {
                    _logger.LogError("Inner exception during form submission: {InnerExceptionType}: {InnerExceptionMessage}", 
                        ex.InnerException.GetType().Name, ex.InnerException.Message);
                }
            }
            
            // Update status to failed
            try
            {
                var submission = await _context.FormSubmissions
                    .FirstOrDefaultAsync(s => s.SubmissionId == submissionId);
                if (submission != null)
                {
                    submission.Status = FormSubmissionStatus.Failed;
                    LogSubmissionAction(submission.Id, "SubmissionFailed", ex.Message);
                    await _context.SaveChangesAsync();
                }
            }
            catch (Exception logEx)
            {
                // Enhanced exception handling for failure logging with DbUpdateException specifics
                if (logEx is DbUpdateException logDbEx)
                {
                    if (logDbEx.InnerException?.Message?.Contains("FOREIGN KEY constraint failed") == true)
                    {
                        _logger.LogError(logDbEx, "FOREIGN KEY constraint failed while logging submission failure for {SubmissionId}. SQLite Error 19 detected. Inner exception: {InnerExceptionMessage}",
                            submissionId, logDbEx.InnerException?.Message);
                    }
                    else
                    {
                        _logger.LogError(logDbEx, "DbUpdateException while logging submission failure for {SubmissionId}. Inner exception: {InnerExceptionMessage}",
                            submissionId, logDbEx.InnerException?.Message);
                    }
                }
                else
                {
                    // Log the failure to update submission status with full details
                    _logger.LogError(logEx, "Failed to log submission failure for {SubmissionId}. Exception type: {ExceptionType}, Message: {ExceptionMessage}, StackTrace: {StackTrace}",
                        submissionId, logEx.GetType().Name, logEx.Message, logEx.StackTrace);
                }
            }

            return new FormSubmissionResponse
            {
                Message = errorMessage,
                Success = false
            };
        }
    }

    public async Task<FormSubmissionResponse> ProcessFormDirectAsync(FormData formData, string clientIpAddress)
    {
        try
        {
            var submissionId = Guid.NewGuid().ToString();
            var submissionTime = DateTime.UtcNow;
            
            // Create submission record
            var submission = new FormSubmissionEntity
            {
                SubmissionId = submissionId,
                UserEmail = formData.TenantDetails.Email,
                FormDataJson = JsonSerializer.Serialize(formData, new JsonSerializerOptions { WriteIndented = true }),
                ClientIpAddress = clientIpAddress,
                Status = FormSubmissionStatus.Submitted,
                EmailVerified = false, // Direct submission bypasses email verification
                SubmittedAt = submissionTime
            };

            // FIXED: Create the initial log entry and add it to the submission's navigation property
            var initialLog = new FormSubmissionLog
            {
                Action = "DirectSubmission",
                Details = $"Form submitted directly via API from IP: {clientIpAddress}",
                Timestamp = DateTime.UtcNow
            };
            
            submission.Logs.Add(initialLog);
            _context.FormSubmissions.Add(submission);
            
            // Save submission and initial log in a single transaction
            await _context.SaveChangesAsync();

            // Generate PDF with audit trail information
            // DEBUG: Enhanced PDF generation logging for direct submission to browser console (production: remove DEBUG prefix)
            await _debugConsole.LogInfoAsync("DIRECT FORM SUBMISSION: PDF GENERATION");
            await _debugConsole.LogAsync($"Starting PDF generation for direct submission {submissionId}");
            
            Console.WriteLine("=== DIRECT FORM SUBMISSION: PDF GENERATION ===");
            Console.WriteLine($"Starting PDF generation for direct submission {submissionId}");
            _logger.LogInformation("DEBUG - Starting PDF generation for direct submission {SubmissionId}", submissionId);
            
            var pdfData = await _pdfService.GenerateFormPdfAsync(formData, submissionId, submissionTime, clientIpAddress);
            var fileName = _pdfService.GenerateFileName(formData, submissionTime);
            
            submission.PdfFileName = fileName;
            submission.Status = FormSubmissionStatus.PdfGenerated;

            LogSubmissionAction(submission.Id, "PdfGenerated", $"PDF generated: {fileName}");

            // Upload to blob storage
            // DEBUG: Enhanced blob upload logging for direct submission to browser console (production: remove DEBUG prefix)
            await _debugConsole.LogInfoAsync("DIRECT FORM SUBMISSION: BLOB UPLOAD");
            await _debugConsole.LogAsync($"Starting blob upload for direct submission {submissionId}, file: {fileName}");
            
            Console.WriteLine("=== DIRECT FORM SUBMISSION: BLOB UPLOAD ===");
            Console.WriteLine($"Starting blob upload for direct submission {submissionId}, file: {fileName}");
            _logger.LogInformation("DEBUG - Starting blob upload for direct submission {SubmissionId}, file {FileName}", submissionId, fileName);
            
            var blobUrl = await _blobService.UploadFormPdfAsync(pdfData, fileName, submissionId);
            submission.BlobStorageUrl = blobUrl;

            LogSubmissionAction(submission.Id, "PdfUploaded", $"PDF uploaded to: {blobUrl}");

            // Send confirmation emails
            // DEBUG: Enhanced email sending logging for direct submission to browser console (production: remove DEBUG prefix)
            await _debugConsole.LogInfoAsync("DIRECT FORM SUBMISSION: EMAIL SENDING");
            await _debugConsole.LogAsync($"Starting email send for direct submission {submissionId} to user: {submission.UserEmail}");
            
            Console.WriteLine("=== DIRECT FORM SUBMISSION: EMAIL SENDING ===");
            Console.WriteLine($"Starting email send for direct submission {submissionId} to user: {submission.UserEmail}");
            _logger.LogInformation("DEBUG - Starting email send for direct submission {SubmissionId} to user {UserEmail}", submissionId, submission.UserEmail);
            
            var userEmailSent = await _emailService.SendFormSubmissionConfirmationAsync(
                submission.UserEmail, submissionId, pdfData, fileName);

            await _debugConsole.LogAsync($"Sending company notification email for direct submission {submissionId}");
            Console.WriteLine($"Sending company notification email for direct submission {submissionId}");
            var companyEmailSent = await _emailService.SendFormSubmissionToCompanyAsync(
                submissionId, pdfData, fileName, submission.UserEmail);

            if (userEmailSent && companyEmailSent)
            {
                submission.Status = FormSubmissionStatus.Completed;
                LogSubmissionAction(submission.Id, "EmailsSent", "Confirmation emails sent successfully");
            }
            else
            {
                LogSubmissionAction(submission.Id, "EmailSendFailed", 
                    $"Email send status - User: {userEmailSent}, Company: {companyEmailSent}");
            }

            await _context.SaveChangesAsync();

            _logger.LogInformation("Direct form submission completed successfully for submission {SubmissionId}", submissionId);

            return new FormSubmissionResponse
            {
                SubmissionId = submissionId,
                Status = submission.Status,
                Message = "Form submitted and processed successfully",
                Success = true
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process direct form submission for user {Email}", formData?.TenantDetails?.Email);
            
            // Enhanced error handling with specific failure details
            var errorMessage = "An error occurred while processing your submission";
            var errorDetails = ex.Message;
            
            // Provide more specific error messages based on exception type
            if (ex is DbUpdateException dbEx)
            {
                if (dbEx.InnerException?.Message?.Contains("FOREIGN KEY constraint failed") == true)
                {
                    errorMessage = "Database constraint error occurred during submission";
                    errorDetails = "Foreign key constraint failure - this is likely a data integrity issue";
                }
                else if (dbEx.InnerException?.Message?.Contains("UNIQUE constraint failed") == true)
                {
                    errorMessage = "Duplicate submission detected";
                    errorDetails = "A submission with similar data already exists";
                }
                else
                {
                    errorMessage = "Database error occurred during submission";
                    errorDetails = dbEx.InnerException?.Message ?? dbEx.Message;
                }
            }
            else if (ex is HttpRequestException || ex.Message.Contains("network") || ex.Message.Contains("connection"))
            {
                errorMessage = "Network connectivity issue occurred";
                errorDetails = "Failed to connect to external services (email or storage)";
            }
            else if (ex.Message.Contains("blob") || ex.Message.Contains("storage"))
            {
                errorMessage = "File storage error occurred";
                errorDetails = "Failed to save form document to storage";
            }
            else if (ex.Message.Contains("email") || ex.Message.Contains("smtp"))
            {
                errorMessage = "Email delivery error occurred";
                errorDetails = "Failed to send confirmation emails";
            }
            else if (ex.Message.Contains("pdf") || ex.Message.Contains("generation"))
            {
                errorMessage = "Document generation error occurred";
                errorDetails = "Failed to generate PDF document from form data";
            }
            
            // Log the detailed error for debugging
            _logger.LogError("Direct form submission failed with error: {ErrorMessage}. Details: {ErrorDetails}. Exception: {Exception}", 
                errorMessage, errorDetails, ex.ToString());
            
            Console.WriteLine($"=== DIRECT FORM SUBMISSION FAILED ===");
            Console.WriteLine($"Error Message: {errorMessage}");
            Console.WriteLine($"Error Details: {errorDetails}");
            Console.WriteLine($"Exception Type: {ex.GetType().Name}");
            Console.WriteLine($"Exception Message: {ex.Message}");
            if (ex.InnerException != null)
            {
                Console.WriteLine($"Inner Exception: {ex.InnerException.GetType().Name}: {ex.InnerException.Message}");
            }
            Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            
            return new FormSubmissionResponse
            {
                Message = $"{errorMessage}. {errorDetails}",
                Success = false
            };
        }
    }

    public async Task<FormSubmissionEntity?> GetSubmissionAsync(string submissionId)
    {
        return await _context.FormSubmissions
            .Include(s => s.Logs)
            .FirstOrDefaultAsync(s => s.SubmissionId == submissionId);
    }

    private void LogSubmissionAction(int submissionId, string action, string? details = null)
    {
        // FIXED: Add defensive check to ensure submission ID is valid
        if (submissionId <= 0)
        {
            _logger.LogError("Cannot log action '{Action}' - invalid submission ID: {SubmissionId}", action, submissionId);
            return;
        }

        var log = new FormSubmissionLog
        {
            FormSubmissionId = submissionId,
            Action = action,
            Details = details,
            Timestamp = DateTime.UtcNow
        };

        _context.FormSubmissionLogs.Add(log);
    }

    private string GenerateVerificationToken()
    {
        var random = new Random();
        var token = new char[_appSettings.TokenLength];
        
        for (int i = 0; i < _appSettings.TokenLength; i++)
        {
            token[i] = (char)('0' + random.Next(0, 10));
        }
        
        return new string(token);
    }
}