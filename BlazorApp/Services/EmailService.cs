using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Options;
using MimeKit;
using System.Linq;

namespace BlazorApp.Services;

public interface IEmailService
{
    Task<bool> SendEmailVerificationTokenAsync(string email, string token, string submissionId);
    Task<bool> SendFormSubmissionConfirmationAsync(string email, string submissionId, byte[] pdfData, string fileName);
    Task<bool> SendFormSubmissionToCompanyAsync(string submissionId, byte[] pdfData, string fileName, string userEmail);
}

public class EmailService : IEmailService
{
    private readonly EmailSettings _emailSettings;
    private readonly ApplicationSettings _appSettings;
    private readonly ILogger<EmailService> _logger;
    private readonly IDebugConsoleHelper _debugConsole;

    public EmailService(
        IOptions<EmailSettings> emailSettings,
        IOptions<ApplicationSettings> appSettings,
        ILogger<EmailService> logger,
        IDebugConsoleHelper debugConsole)
    {
        _emailSettings = emailSettings.Value;
        _appSettings = appSettings.Value;
        _logger = logger;
        _debugConsole = debugConsole;
    }

    public async Task<bool> SendEmailVerificationTokenAsync(string email, string token, string submissionId)
    {
        try
        {
            var message = new MimeMessage();
            message.From.Add(new MailboxAddress(_emailSettings.FromName, _emailSettings.FromEmail));
            message.To.Add(new MailboxAddress("", email));
            message.Subject = "Email Verification - Accommodation Form";

            var bodyBuilder = new BodyBuilder
            {
                HtmlBody = $@"
                <html>
                <body>
                    <h2>Email Verification Required</h2>
                    <p>Dear Applicant,</p>
                    <p>To complete your accommodation application, please enter the following verification code:</p>
                    <h1 style='color: #007acc; font-family: monospace; font-size: 32px; text-align: center; 
                              background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;'>{token}</h1>
                    <p><strong>Submission ID:</strong> {submissionId}</p>
                    <p>This code will expire in {_appSettings.TokenExpirationMinutes} minutes.</p>
                    <p>If you did not request this verification, please ignore this email.</p>
                    <br>
                    <p>Best regards,<br>
                    {_appSettings.ApplicationName}</p>
                </body>
                </html>",
                TextBody = $@"
Email Verification Required

Dear Applicant,

To complete your accommodation application, please enter the following verification code: {token}

Submission ID: {submissionId}

This code will expire in {_appSettings.TokenExpirationMinutes} minutes.

If you did not request this verification, please ignore this email.

Best regards,
{_appSettings.ApplicationName}"
            };

            message.Body = bodyBuilder.ToMessageBody();

            return await SendEmailAsync(message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send email verification token to {Email}", email);
            return false;
        }
    }

    public async Task<bool> SendFormSubmissionConfirmationAsync(string email, string submissionId, byte[] pdfData, string fileName)
    {
        try
        {
            var message = new MimeMessage();
            message.From.Add(new MailboxAddress(_emailSettings.FromName, _emailSettings.FromEmail));
            message.To.Add(new MailboxAddress("", email));
            message.Subject = "Accommodation Application Submitted";

            var bodyBuilder = new BodyBuilder
            {
                HtmlBody = $@"
                <html>
                <body>
                    <h2>Application Submitted Successfully</h2>
                    <p>Dear Applicant,</p>
                    <p>Thank you for submitting your accommodation application. Your submission has been received and processed.</p>
                    <p><strong>Submission ID:</strong> {submissionId}</p>
                    <p><strong>Submitted:</strong> {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC</p>
                    <p>Please find your completed application form attached to this email.</p>
                    <p>We will review your application and contact you soon.</p>
                    <br>
                    <p>Best regards,<br>
                    {_appSettings.ApplicationName}</p>
                </body>
                </html>",
                TextBody = $@"
Application Submitted Successfully

Dear Applicant,

Thank you for submitting your accommodation application. Your submission has been received and processed.

Submission ID: {submissionId}
Submitted: {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC

Please find your completed application form attached to this email.

We will review your application and contact you soon.

Best regards,
{_appSettings.ApplicationName}"
            };

            // Attach PDF
            bodyBuilder.Attachments.Add(fileName, pdfData, ContentType.Parse("application/pdf"));

            message.Body = bodyBuilder.ToMessageBody();

            return await SendEmailAsync(message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send form submission confirmation to {Email}", email);
            return false;
        }
    }

    public async Task<bool> SendFormSubmissionToCompanyAsync(string submissionId, byte[] pdfData, string fileName, string userEmail)
    {
        try
        {
            var message = new MimeMessage();
            message.From.Add(new MailboxAddress(_emailSettings.FromName, _emailSettings.FromEmail));
            message.To.Add(new MailboxAddress("", _emailSettings.CompanyEmail));
            message.Subject = $"New Accommodation Application - {submissionId}";

            var bodyBuilder = new BodyBuilder
            {
                HtmlBody = $@"
                <html>
                <body>
                    <h2>New Accommodation Application Received</h2>
                    <p><strong>Submission ID:</strong> {submissionId}</p>
                    <p><strong>User Email:</strong> {userEmail}</p>
                    <p><strong>Submitted:</strong> {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC</p>
                    <p>Please find the completed application form attached.</p>
                    <br>
                    <p>Regards,<br>
                    {_appSettings.ApplicationName} System</p>
                </body>
                </html>",
                TextBody = $@"
New Accommodation Application Received

Submission ID: {submissionId}
User Email: {userEmail}
Submitted: {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC

Please find the completed application form attached.

Regards,
{_appSettings.ApplicationName} System"
            };

            // Attach PDF
            bodyBuilder.Attachments.Add(fileName, pdfData, ContentType.Parse("application/pdf"));

            message.Body = bodyBuilder.ToMessageBody();

            return await SendEmailAsync(message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send form submission to company email");
            return false;
        }
    }

    private async Task<bool> SendEmailAsync(MimeMessage message)
    {
        try
        {
            // DEBUG: Log email configuration to browser console (production: remove this section)
            await _debugConsole.LogGroupAsync("EMAIL DEBUG INFO").ConfigureAwait(false);
            await _debugConsole.LogAsync($"SMTP Server: {_emailSettings.SmtpServer}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"SMTP Port: {_emailSettings.SmtpPort}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Use SSL: {_emailSettings.UseSsl}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Username: {_emailSettings.SmtpUsername}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Password: {(!string.IsNullOrEmpty(_emailSettings.SmtpPassword) ? "***CONFIGURED***" : "***NOT SET***")}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"From Email: {_emailSettings.FromEmail}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"From Name: {_emailSettings.FromName}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Company Email: {_emailSettings.CompanyEmail}").ConfigureAwait(false);
            await _debugConsole.LogGroupEndAsync().ConfigureAwait(false);

            // DEBUG: Log email configuration (production: remove this section)
            Console.WriteLine("=== EMAIL DEBUG INFO ===");
            Console.WriteLine($"SMTP Server: {_emailSettings.SmtpServer}");
            Console.WriteLine($"SMTP Port: {_emailSettings.SmtpPort}");
            Console.WriteLine($"Use SSL: {_emailSettings.UseSsl}");
            Console.WriteLine($"Username: {_emailSettings.SmtpUsername}");
            Console.WriteLine($"Password: {(!string.IsNullOrEmpty(_emailSettings.SmtpPassword) ? "***CONFIGURED***" : "***NOT SET***")}");
            Console.WriteLine($"From Email: {_emailSettings.FromEmail}");
            Console.WriteLine($"From Name: {_emailSettings.FromName}");
            Console.WriteLine($"Company Email: {_emailSettings.CompanyEmail}");

            _logger.LogInformation("DEBUG - Email configuration: Server={SmtpServer}, Port={SmtpPort}, SSL={UseSsl}, Username={Username}, FromEmail={FromEmail}",
                _emailSettings.SmtpServer, _emailSettings.SmtpPort, _emailSettings.UseSsl, _emailSettings.SmtpUsername, _emailSettings.FromEmail);

            // DEBUG: Log email message details to browser console (production: remove this section)
            await _debugConsole.LogGroupAsync("EMAIL MESSAGE DEBUG").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Subject: {message.Subject}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"From: {string.Join(", ", message.From)}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"To: {string.Join(", ", message.To)}").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Attachment count: {message.Attachments.Count()}").ConfigureAwait(false);
            
            var attachmentNames = message.Attachments.Select(a => a.ContentDisposition?.FileName ?? "unnamed").ToList();
            if (attachmentNames.Any())
            {
                await _debugConsole.LogAsync($"Attachment names: {string.Join(", ", attachmentNames)}").ConfigureAwait(false);
            }
            await _debugConsole.LogGroupEndAsync().ConfigureAwait(false);

            // DEBUG: Log email message details (production: remove this section)
            Console.WriteLine("=== EMAIL MESSAGE DEBUG ===");
            Console.WriteLine($"Subject: {message.Subject}");
            Console.WriteLine($"From: {string.Join(", ", message.From)}");
            Console.WriteLine($"To: {string.Join(", ", message.To)}");
            Console.WriteLine($"Attachment count: {message.Attachments.Count()}");
            
            if (attachmentNames.Any())
            {
                Console.WriteLine($"Attachment names: {string.Join(", ", attachmentNames)}");
            }
            
            // DEBUG: Log email body content (production: remove this section)
            if (message.Body is MimeKit.Multipart multipart)
            {
                foreach (var part in multipart)
                {
                    if (part is MimeKit.TextPart textPart)
                    {
                        if (textPart.IsHtml)
                        {
                            Console.WriteLine($"Body (HTML): {textPart.Text}");
                        }
                        else
                        {
                            Console.WriteLine($"Body (Text): {textPart.Text}");
                        }
                    }
                }
            }
            else if (message.Body is MimeKit.TextPart singlePart)
            {
                if (singlePart.IsHtml)
                {
                    Console.WriteLine($"Body (HTML): {singlePart.Text}");
                }
                else
                {
                    Console.WriteLine($"Body (Text): {singlePart.Text}");
                }
            }

            _logger.LogInformation("DEBUG - Email message: Subject={Subject}, From={From}, To={To}, AttachmentCount={AttachmentCount}",
                message.Subject, string.Join(", ", message.From), string.Join(", ", message.To), message.Attachments.Count());

            using var client = new SmtpClient();
            
            await client.ConnectAsync(_emailSettings.SmtpServer, _emailSettings.SmtpPort, 
                _emailSettings.UseSsl ? SecureSocketOptions.StartTls : SecureSocketOptions.None).ConfigureAwait(false);

            if (!string.IsNullOrEmpty(_emailSettings.SmtpUsername))
            {
                await client.AuthenticateAsync(_emailSettings.SmtpUsername, _emailSettings.SmtpPassword).ConfigureAwait(false);
            }

            await client.SendAsync(message).ConfigureAwait(false);
            await client.DisconnectAsync(true).ConfigureAwait(false);

            // DEBUG: Log successful send to browser console (production: remove this section)
            await _debugConsole.LogInfoAsync("EMAIL SENT SUCCESSFULLY").ConfigureAwait(false);
            await _debugConsole.LogAsync($"Email sent successfully to {string.Join(", ", message.To)}").ConfigureAwait(false);

            // DEBUG: Log successful send (production: remove this section)
            Console.WriteLine("=== EMAIL SENT SUCCESSFULLY ===");
            _logger.LogInformation("DEBUG - Email sent successfully to {Recipients}", string.Join(", ", message.To));

            return true;
        }
        catch (Exception ex)
        {
            // DEBUG: Enhanced error logging to browser console (production: keep but remove DEBUG prefix)
            await _debugConsole.LogErrorAsync("EMAIL SEND FAILED").ConfigureAwait(false);
            await _debugConsole.LogErrorAsync($"Error: {ex.Message}").ConfigureAwait(false);
            
            // DEBUG: Enhanced error logging (production: keep but remove DEBUG prefix)
            Console.WriteLine($"=== EMAIL SEND FAILED ===");
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            
            _logger.LogError(ex, "Failed to send email via SMTP");
            return false;
        }
    }
}