"""
Email service for sending notifications and MFA tokens

This service uses the email configuration from the settings that mirror
the .NET EmailSettings structure from appsettings.json.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional, BinaryIO
from datetime import datetime

from app.core.config import get_settings
from app.models.form import AccommodationFormData

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails using SMTP configuration that mirrors .NET EmailSettings"""
    
    def __init__(self):
        settings = get_settings()
        self.email_settings = settings.email_settings
        
        # Email server configuration
        self.smtp_server = self.email_settings.smtp_server
        self.smtp_port = self.email_settings.smtp_port
        self.smtp_username = self.email_settings.smtp_username
        self.smtp_password = self.email_settings.smtp_password
        self.use_ssl = self.email_settings.use_ssl  # Maps to UseSsl in .NET
        self.from_email = self.email_settings.from_email
        self.from_name = self.email_settings.from_name
        self.company_email = self.email_settings.company_email  # Maps to CompanyEmail in .NET
        
        logger.info(f"Email service initialized with SMTP server: {self.smtp_server}:{self.smtp_port}")
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        attachments: Optional[list] = None
    ) -> bool:
        """Send email via SMTP using configuration that mirrors .NET EmailSettings"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text part
            msg.attach(MIMEText(body_text, 'plain'))
            
            # Add HTML part if provided
            if body_html:
                msg.attach(MIMEText(body_html, 'html'))
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    msg.attach(attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_ssl:  # Using the .NET compatible property name
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_mfa_token(self, email: str, token: str) -> bool:
        """Send MFA verification token"""
        try:
            # Get current settings to access MFA token expiry
            settings = get_settings()
            
            subject = "Your Accommodation Form Verification Code"
            
            body_text = f"""
Your verification code for the Azure Accommodation Form is: {token}

This code will expire in {settings.mfa_token_expiry_minutes} minutes.

If you did not request this code, please ignore this email.

Best regards,
Azure Accommodation Form Team
            """.strip()
            
            body_html = f"""
            <html>
            <body>
                <h2>Verification Code</h2>
                <p>Your verification code for the Azure Accommodation Form is:</p>
                <h1 style="color: #007acc; font-family: monospace; letter-spacing: 2px;">{token}</h1>
                <p>This code will expire in <strong>{settings.mfa_token_expiry_minutes} minutes</strong>.</p>
                <p>If you did not request this code, please ignore this email.</p>
                <hr>
                <p><em>Azure Accommodation Form Team</em></p>
            </body>
            </html>
            """
            
            return await self._send_email(email, subject, body_text, body_html)
            
        except Exception as e:
            logger.error(f"Failed to send MFA token to {email}: {e}")
            return False
    
    async def send_form_confirmation(
        self,
        to_email: str,
        form_data: AccommodationFormData,
        pdf_buffer: BinaryIO,
        pdf_filename: str
    ) -> bool:
        """Send form submission confirmation to user"""
        subject = "Accommodation Form Submission Confirmation"
        
        tenant_name = form_data.tenant_details.full_name
        submission_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        body_text = f"""
Dear {tenant_name},

Thank you for submitting your accommodation application form.

Your application has been received and is being processed. You will receive a response within 2-3 business days.

Submission Details:
- Name: {tenant_name}
- Email: {to_email}
- Submitted: {submission_time}
- Application ID: {pdf_filename.replace('.pdf', '')}

Please find your completed application form attached to this email for your records.

If you have any questions, please contact us at {self.company_email or 'admin@yourdomain.com'}.

Best regards,
Azure Accommodation Team
        """.strip()
        
        body_html = f"""
        <html>
        <body>
            <h2>Accommodation Application Confirmation</h2>
            <p>Dear <strong>{tenant_name}</strong>,</p>
            <p>Thank you for submitting your accommodation application form.</p>
            <p>Your application has been received and is being processed. You will receive a response within <strong>2-3 business days</strong>.</p>
            
            <h3>Submission Details:</h3>
            <ul>
                <li><strong>Name:</strong> {tenant_name}</li>
                <li><strong>Email:</strong> {to_email}</li>
                <li><strong>Submitted:</strong> {submission_time}</li>
                <li><strong>Application ID:</strong> {pdf_filename.replace('.pdf', '')}</li>
            </ul>
            
            <p>Please find your completed application form attached to this email for your records.</p>
            <p>If you have any questions, please contact us at <a href="mailto:{self.company_email or 'admin@yourdomain.com'}">{self.company_email or 'admin@yourdomain.com'}</a>.</p>
            
            <hr>
            <p><em>Azure Accommodation Team</em></p>
        </body>
        </html>
        """
        
        # Create PDF attachment
        pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), _subtype='pdf')
        pdf_attachment.add_header(
            'Content-Disposition', 
            'attachment', 
            filename=pdf_filename
        )
        
        return await self._send_email(
            to_email, 
            subject, 
            body_text, 
            body_html, 
            attachments=[pdf_attachment]
        )
    
    async def send_admin_notification(
        self,
        form_data: AccommodationFormData,
        pdf_buffer: BinaryIO,
        pdf_filename: str,
        blob_url: str
    ) -> bool:
        """Send new submission notification to admin"""
        subject = f"New Accommodation Application - {form_data.tenant_details.full_name}"
        
        tenant = form_data.tenant_details
        submission_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        body_text = f"""
New accommodation application received:

Applicant Details:
- Name: {tenant.full_name}
- Email: {tenant.email}
- Phone: {tenant.telephone}
- Date of Birth: {tenant.date_of_birth}
- Employer: {tenant.employers_name}

Application Details:
- Submitted: {submission_time}
- Client IP: {form_data.client_ip}
- Application ID: {pdf_filename.replace('.pdf', '')}

Bank Details:
- Bank: {form_data.bank_details.bank_name}
- Account: {form_data.bank_details.account_no}
- Sort Code: {form_data.bank_details.sort_code}

Current Employment:
- Job Title: {form_data.employment.job_title}
- Salary: £{form_data.employment.present_salary:,.2f}

The complete application form is attached.
Azure Blob Storage URL: {blob_url}

Please review and process this application.
        """.strip()
        
        body_html = f"""
        <html>
        <body>
            <h2>New Accommodation Application</h2>
            
            <h3>Applicant Details:</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Name:</strong></td><td>{tenant.full_name}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{tenant.email}</td></tr>
                <tr><td><strong>Phone:</strong></td><td>{tenant.telephone}</td></tr>
                <tr><td><strong>Date of Birth:</strong></td><td>{tenant.date_of_birth}</td></tr>
                <tr><td><strong>Employer:</strong></td><td>{tenant.employers_name}</td></tr>
            </table>
            
            <h3>Application Details:</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Submitted:</strong></td><td>{submission_time}</td></tr>
                <tr><td><strong>Client IP:</strong></td><td>{form_data.client_ip}</td></tr>
                <tr><td><strong>Application ID:</strong></td><td>{pdf_filename.replace('.pdf', '')}</td></tr>
            </table>
            
            <h3>Bank Details:</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Bank:</strong></td><td>{form_data.bank_details.bank_name}</td></tr>
                <tr><td><strong>Account:</strong></td><td>{form_data.bank_details.account_no}</td></tr>
                <tr><td><strong>Sort Code:</strong></td><td>{form_data.bank_details.sort_code}</td></tr>
            </table>
            
            <h3>Current Employment:</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Job Title:</strong></td><td>{form_data.employment.job_title}</td></tr>
                <tr><td><strong>Salary:</strong></td><td>£{form_data.employment.present_salary:,.2f}</td></tr>
            </table>
            
            <p>The complete application form is attached.</p>
            <p><strong>Azure Blob Storage URL:</strong> <a href="{blob_url}">{blob_url}</a></p>
            
            <p>Please review and process this application.</p>
            
            <hr>
            <p><em>Azure Accommodation Form System</em></p>
        </body>
        </html>
        """
        
        # Create PDF attachment
        pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), _subtype='pdf')
        pdf_attachment.add_header(
            'Content-Disposition', 
            'attachment', 
            filename=pdf_filename
        )
        
        return await self._send_email(
            self.company_email or 'admin@yourdomain.com', 
            subject, 
            body_text, 
            body_html, 
            attachments=[pdf_attachment]
        )