"""
Form processing routes
"""

import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status, Depends, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse

from app.core.security import get_current_ip, require_certificate_auth
from app.core.config import get_settings
from app.models.form import (
    AccommodationFormData,
    FormSubmissionRequest,
    FormSubmissionResponse
)
from app.services.form import FormService
from app.services.pdf import PDFGenerationService
from app.services.email import EmailService
from app.services.storage import AzureBlobStorageService
from app.services.session import SessionService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

@router.post("/initialize")
async def initialize_form(request: Request):
    """Initialize a new form session"""
    require_certificate_auth(request)
    
    client_ip = get_current_ip(request)
    session_id = request.headers.get("X-Session-Token")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid session required"
        )
    
    # Verify session
    session_service = SessionService()
    session = await session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    form_service = FormService()
    form_session = await form_service.create_form_session(
        email=session["email"],
        client_ip=client_ip
    )
    
    logger.info(f"Form session initialized for {session['email']} from IP: {client_ip}")
    
    return {
        "form_session_id": form_session["id"],
        "email": session["email"],
        "client_ip": client_ip,
        "initialized_at": form_session["created_at"]
    }

@router.post("/submit", response_model=FormSubmissionResponse)
async def submit_form(
    request: Request
):
    """Submit the completed accommodation form"""
    require_certificate_auth(request)
    
    client_ip = get_current_ip(request)
    session_id = request.headers.get("X-Session-Token")
    
    # Log incoming request for debugging
    logger.info(f"Form submission attempt from IP: {client_ip}")
    
    # Parse request body manually to get better error details
    try:
        raw_body = await request.body()
        body_str = raw_body.decode('utf-8')
        logger.info(f"Raw request body: {body_str}")
        
        import json
        request_data = json.loads(body_str)
        logger.info(f"Parsed request data keys: {list(request_data.keys())}")
        
        # First try to validate as FormSubmissionRequest if it has the right structure
        if "form_data" in request_data:
            # This is the proper FormSubmissionRequest structure
            try:
                submission_request = FormSubmissionRequest(**request_data)
                form_data = submission_request.form_data
                logger.info("FormSubmissionRequest validation successful")
            except Exception as validation_error:
                logger.error(f"FormSubmissionRequest validation failed: {validation_error}")
                logger.error(f"Request data structure: {json.dumps(request_data, indent=2, default=str)}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Form submission validation failed: {str(validation_error)}"
                )
        else:
            # Fallback: try to validate as AccommodationFormData directly (legacy support)
            try:
                form_data = AccommodationFormData(**request_data)
                logger.info("AccommodationFormData validation successful (legacy mode)")
            except Exception as validation_error:
                logger.error(f"Form validation failed: {validation_error}")
                logger.error(f"Request data structure: {json.dumps(request_data, indent=2, default=str)}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Form validation failed: {str(validation_error)}"
                )
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON in request body"
        )
    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request processing error: {str(e)}"
        )
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid session required"
        )
    
    # Verify session
    session_service = SessionService()
    session = await session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    # Verify email matches session
    if form_data.tenant_details.email != session["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form email must match verified session email"
        )
    
    # Add metadata
    form_data.client_ip = client_ip
    form_data.form_submitted_at = datetime.utcnow()
    
    try:
        # Process form submission
        form_service = FormService()
        submission = await form_service.process_submission(form_data)
        
        # Generate PDF
        pdf_service = PDFGenerationService()
        pdf_buffer = await pdf_service.generate_pdf(form_data)
        
        # Generate filename
        pdf_filename = await pdf_service.generate_filename(form_data)
        
        # Store PDF in Azure Blob Storage
        storage_service = AzureBlobStorageService()
        blob_url = await storage_service.upload_pdf(pdf_filename, pdf_buffer)
        
        # Send emails
        email_service = EmailService()
        
        # Send to user
        await email_service.send_form_confirmation(
            to_email=form_data.tenant_details.email,
            form_data=form_data,
            pdf_buffer=pdf_buffer,
            pdf_filename=pdf_filename
        )
        
        # Send to admin
        await email_service.send_admin_notification(
            form_data=form_data,
            pdf_buffer=pdf_buffer,
            pdf_filename=pdf_filename,
            blob_url=blob_url
        )
        
        # Update submission record
        await form_service.update_submission_status(
            submission["id"],
            "completed",
            pdf_filename=pdf_filename,
            blob_url=blob_url
        )
        
        logger.info(f"Form submission completed: {submission['id']}")
        
        return FormSubmissionResponse(
            submission_id=submission["id"],
            status="success",
            message="Form submitted successfully",
            pdf_filename=pdf_filename,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Form submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Form submission failed. Please try again."
        )

@router.get("/submission/{submission_id}/status")
async def get_submission_status(
    submission_id: str,
    request: Request
):
    """Get the status of a form submission"""
    require_certificate_auth(request)
    
    session_id = request.headers.get("X-Session-Token")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid session required"
        )
    
    # Verify session
    session_service = SessionService()
    session = await session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    form_service = FormService()
    submission = await form_service.get_submission(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Verify user can access this submission
    if submission["email"] != session["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "submission_id": submission["id"],
        "status": submission["status"],
        "submitted_at": submission["created_at"],
        "pdf_filename": submission.get("pdf_filename"),
        "client_ip": submission.get("client_ip")
    }

@router.get("/download/{submission_id}")
async def download_submission_pdf(
    submission_id: str,
    request: Request
):
    """Download the PDF for a submission (user access only)"""
    require_certificate_auth(request)
    
    session_id = request.headers.get("X-Session-Token")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid session required"
        )
    
    # Verify session
    session_service = SessionService()
    session = await session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    form_service = FormService()
    submission = await form_service.get_submission(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Verify user can access this submission
    if submission["email"] != session["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get PDF from Azure Blob Storage
    storage_service = AzureBlobStorageService()
    pdf_data = await storage_service.download_pdf(submission["pdf_filename"])
    
    # Return as file download
    return FileResponse(
        path=pdf_data,
        filename=submission["pdf_filename"],
        media_type="application/pdf"
    )