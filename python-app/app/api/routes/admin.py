"""
Admin routes for form management
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, EmailStr

from app.core.security import get_current_ip, require_certificate_auth
from app.core.config import get_settings
from app.services.form import FormService
from app.services.storage import AzureBlobStorageService
from app.services.email import EmailService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

class TestEmailRequest(BaseModel):
    """Request model for test email endpoint"""
    to_email: EmailStr
    message: Optional[str] = "This is a test email from the Azure Accommodation Form application."

# Admin authentication (placeholder - implement proper admin auth)
async def verify_admin_access(request: Request):
    """Verify admin access (placeholder implementation)"""
    require_certificate_auth(request)
    
    # In production, implement proper admin authentication
    admin_token = request.headers.get("X-Admin-Token")
    
    if not admin_token or admin_token != os.getenv("ADMIN_TOKEN", "admin-secret"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

@router.get("/submissions")
async def list_submissions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None)
):
    """List form submissions (admin only)"""
    await verify_admin_access(request)
    
    form_service = FormService()
    submissions = await form_service.list_submissions(
        page=page,
        limit=limit,
        status_filter=status_filter,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "submissions": submissions["items"],
        "total": submissions["total"],
        "page": page,
        "limit": limit,
        "total_pages": (submissions["total"] + limit - 1) // limit
    }

@router.get("/submissions/{submission_id}")
async def get_submission_details(
    submission_id: str,
    request: Request
):
    """Get detailed submission information (admin only)"""
    await verify_admin_access(request)
    
    form_service = FormService()
    submission = await form_service.get_submission_with_details(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    return submission

@router.get("/submissions/{submission_id}/download")
async def download_submission_admin(
    submission_id: str,
    request: Request
):
    """Download submission PDF (admin only)"""
    await verify_admin_access(request)
    
    form_service = FormService()
    submission = await form_service.get_submission(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Get PDF from Azure Blob Storage
    storage_service = AzureBlobStorageService()
    pdf_data = await storage_service.download_pdf(submission["pdf_filename"])
    
    return FileResponse(
        path=pdf_data,
        filename=submission["pdf_filename"],
        media_type="application/pdf"
    )

@router.get("/stats")
async def get_statistics(
    request: Request,
    days: int = Query(30, ge=1, le=365)
):
    """Get submission statistics (admin only)"""
    await verify_admin_access(request)
    
    form_service = FormService()
    stats = await form_service.get_statistics(days=days)
    
    return stats

@router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: str,
    request: Request
):
    """Delete a submission and its associated files (admin only)"""
    await verify_admin_access(request)
    
    form_service = FormService()
    submission = await form_service.get_submission(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Delete from Azure Blob Storage
    if submission.get("pdf_filename"):
        storage_service = AzureBlobStorageService()
        await storage_service.delete_pdf(submission["pdf_filename"])
    
    # Delete submission record
    await form_service.delete_submission(submission_id)
    
    logger.info(f"Submission {submission_id} deleted by admin")
    
    return {"message": "Submission deleted successfully"}

@router.post("/submissions/{submission_id}/resend-email")
async def resend_confirmation_email(
    submission_id: str,
    request: Request
):
    """Resend confirmation email for a submission (admin only)"""
    await verify_admin_access(request)
    
    form_service = FormService()
    submission = await form_service.get_submission_with_details(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Get PDF from storage
    storage_service = AzureBlobStorageService()
    pdf_buffer = await storage_service.download_pdf_buffer(submission["pdf_filename"])
    
    # Resend email
    email_service = EmailService()
    await email_service.send_form_confirmation(
        to_email=submission["email"],
        form_data=submission["form_data"],
        pdf_buffer=pdf_buffer,
        pdf_filename=submission["pdf_filename"]
    )
    
    logger.info(f"Confirmation email resent for submission {submission_id}")
    
    return {"message": "Confirmation email sent successfully"}

@router.get("/config/email")
async def get_email_configuration(request: Request):
    """Get current email configuration (admin only, excludes secrets)"""
    await verify_admin_access(request)
    
    # Perform configuration audit
    audit_info = settings.audit_configuration(logger)
    
    return {
        "email_config": {
            "smtp_server": settings.email_settings.smtp_server,
            "smtp_port": settings.email_settings.smtp_port,
            "smtp_username": settings.email_settings.smtp_username or "[NOT SET]",
            "smtp_password": "[SET]" if settings.email_settings.smtp_password else "[NOT SET]",
            "use_ssl": settings.email_settings.use_ssl,
            "from_email": settings.email_settings.from_email or "[NOT SET]",
            "from_name": settings.email_settings.from_name,
            "company_email": settings.email_settings.company_email or "[NOT SET]"
        },
        "config_audit": audit_info,
        "ready_for_email": bool(
            settings.email_settings.smtp_username and 
            settings.email_settings.smtp_password and
            settings.email_settings.from_email
        )
    }

@router.post("/config/email/test")
async def send_test_email(
    test_email: TestEmailRequest,
    request: Request
):
    """Send a test email to verify email configuration (admin only)"""
    await verify_admin_access(request)
    
    # Check if email is configured
    if not settings.email_settings.smtp_username or not settings.email_settings.smtp_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email service not configured. Please set SMTP credentials."
        )
    
    try:
        email_service = EmailService()
        
        # Create test email content
        subject = "Test Email from Azure Accommodation Form"
        
        body_text = f"""
This is a test email from the Azure Accommodation Form application.

Configuration Details:
- SMTP Server: {settings.email_settings.smtp_server}:{settings.email_settings.smtp_port}
- From: {settings.email_settings.from_name} <{settings.email_settings.from_email}>
- SSL/TLS: {"Enabled" if settings.email_settings.use_ssl else "Disabled"}

Test Message: {test_email.message}

If you received this email, the email configuration is working correctly.

Sent at: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
        """.strip()
        
        body_html = f"""
        <html>
        <body>
            <h2>Test Email from Azure Accommodation Form</h2>
            <p>This is a test email from the Azure Accommodation Form application.</p>
            
            <h3>Configuration Details:</h3>
            <ul>
                <li><strong>SMTP Server:</strong> {settings.email_settings.smtp_server}:{settings.email_settings.smtp_port}</li>
                <li><strong>From:</strong> {settings.email_settings.from_name} &lt;{settings.email_settings.from_email}&gt;</li>
                <li><strong>SSL/TLS:</strong> {"Enabled" if settings.email_settings.use_ssl else "Disabled"}</li>
            </ul>
            
            <h3>Test Message:</h3>
            <p><em>{test_email.message}</em></p>
            
            <p>If you received this email, the email configuration is working correctly.</p>
            
            <hr>
            <p><small>Sent at: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</small></p>
        </body>
        </html>
        """
        
        # Send test email using the internal _send_email method
        success = await email_service._send_email(
            to_email=test_email.to_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )
        
        if success:
            logger.info(f"Test email sent successfully to {test_email.to_email}")
            return {
                "message": "Test email sent successfully",
                "to_email": test_email.to_email,
                "smtp_server": settings.email_settings.smtp_server,
                "sent_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email. Check server logs for details."
            )
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}"
        )