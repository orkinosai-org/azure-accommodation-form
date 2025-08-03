"""
Admin routes for form management
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse, FileResponse

from app.core.security import get_current_ip, require_certificate_auth
from app.core.config import get_settings
from app.services.form import FormService
from app.services.storage import AzureBlobStorageService
from app.services.email import EmailService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

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