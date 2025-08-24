"""
Admin routes for form management
"""

import os
import logging
import io
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel, EmailStr

from app.core.security import get_current_ip, require_certificate_auth
from app.core.config import get_settings, LogLevel
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

# Log viewing related models
class LogEntry(BaseModel):
    """Model for a single log entry"""
    timestamp: str
    level: str
    logger: str
    message: str
    module: Optional[str] = None
    line_number: Optional[int] = None

class LogLevelUpdate(BaseModel):
    """Model for updating log levels"""
    logger_name: str
    level: str

# In-memory log handler to capture recent logs
class InMemoryLogHandler(logging.Handler):
    """Custom log handler that stores recent logs in memory"""
    
    def __init__(self, max_records: int = 1000):
        super().__init__()
        self.max_records = max_records
        self.records: List[logging.LogRecord] = []
    
    def emit(self, record: logging.LogRecord):
        """Store the log record"""
        self.records.append(record)
        # Keep only the most recent records
        if len(self.records) > self.max_records:
            self.records = self.records[-self.max_records:]
    
    def get_recent_logs(self, count: Optional[int] = None, level_filter: Optional[str] = None) -> List[LogEntry]:
        """Get recent log entries"""
        records = self.records
        
        # Filter by level if specified
        if level_filter:
            level_num = getattr(logging, level_filter.upper(), None)
            if level_num:
                records = [r for r in records if r.levelno >= level_num]
        
        # Limit count if specified
        if count:
            records = records[-count:]
        
        # Convert to LogEntry objects
        log_entries = []
        for record in records:
            try:
                log_entry = LogEntry(
                    timestamp=datetime.fromtimestamp(record.created).isoformat(),
                    level=record.levelname,
                    logger=record.name,
                    message=record.getMessage(),
                    module=getattr(record, 'filename', None),
                    line_number=getattr(record, 'lineno', None)
                )
                log_entries.append(log_entry)
            except Exception as e:
                # If there's an error processing a record, skip it
                continue
        
        return log_entries

# Global in-memory log handler instance
_memory_handler = InMemoryLogHandler()

# Add the memory handler to the root logger if not already added
def _ensure_memory_handler():
    """Ensure the memory handler is added to the root logger"""
    root_logger = logging.getLogger()
    if _memory_handler not in root_logger.handlers:
        _memory_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(_memory_handler)

# Initialize the memory handler
_ensure_memory_handler()

@router.get("/logs")
async def get_application_logs(
    request: Request,
    count: int = Query(100, ge=1, le=1000, description="Number of recent log entries to return"),
    level: Optional[str] = Query(None, description="Minimum log level filter (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    logger_name: Optional[str] = Query(None, description="Filter by specific logger name")
):
    """Get recent application logs (admin only)"""
    await verify_admin_access(request)
    
    _ensure_memory_handler()
    
    try:
        # Get logs from the memory handler
        log_entries = _memory_handler.get_recent_logs(count=count, level_filter=level)
        
        # Filter by logger name if specified
        if logger_name:
            log_entries = [entry for entry in log_entries if logger_name.lower() in entry.logger.lower()]
        
        return {
            "logs": log_entries,
            "total_returned": len(log_entries),
            "filters": {
                "count": count,
                "level": level,
                "logger_name": logger_name
            },
            "available_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving application logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve logs: {str(e)}"
        )

@router.get("/logs/levels")
async def get_log_levels(request: Request):
    """Get current log levels for all active loggers (admin only)"""
    await verify_admin_access(request)
    
    try:
        loggers_info = {}
        
        # Get root logger info
        root_logger = logging.getLogger()
        loggers_info["root"] = {
            "level": logging.getLevelName(root_logger.level),
            "level_number": root_logger.level,
            "handlers": len(root_logger.handlers),
            "effective_level": logging.getLevelName(root_logger.getEffectiveLevel())
        }
        
        # Get info for all known loggers
        logger_dict = logging.Logger.manager.loggerDict
        for name, logger_obj in logger_dict.items():
            if isinstance(logger_obj, logging.Logger):
                loggers_info[name] = {
                    "level": logging.getLevelName(logger_obj.level),
                    "level_number": logger_obj.level,
                    "handlers": len(logger_obj.handlers),
                    "effective_level": logging.getLevelName(logger_obj.getEffectiveLevel()),
                    "propagate": logger_obj.propagate
                }
        
        return {
            "loggers": loggers_info,
            "available_levels": [
                {"name": "DEBUG", "value": logging.DEBUG},
                {"name": "INFO", "value": logging.INFO},
                {"name": "WARNING", "value": logging.WARNING},
                {"name": "ERROR", "value": logging.ERROR},
                {"name": "CRITICAL", "value": logging.CRITICAL}
            ],
            "config_source": "runtime"
        }
        
    except Exception as e:
        logger.error(f"Error getting log levels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get log levels: {str(e)}"
        )

@router.post("/logs/levels")
async def update_log_level(
    log_level_update: LogLevelUpdate,
    request: Request
):
    """Update log level for a specific logger (admin only)"""
    await verify_admin_access(request)
    
    try:
        # Validate the log level
        level_name = log_level_update.level.upper()
        if level_name not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid log level: {log_level_update.level}. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )
        
        # Get the logger
        target_logger = logging.getLogger(log_level_update.logger_name)
        
        # Convert level name to level number
        level_number = getattr(logging, level_name)
        
        # Update the logger level
        old_level = logging.getLevelName(target_logger.level)
        target_logger.setLevel(level_number)
        
        logger.info(f"Updated log level for logger '{log_level_update.logger_name}' from {old_level} to {level_name}")
        
        return {
            "message": f"Updated log level for logger '{log_level_update.logger_name}'",
            "logger_name": log_level_update.logger_name,
            "old_level": old_level,
            "new_level": level_name,
            "new_level_number": level_number
        }
        
    except Exception as e:
        logger.error(f"Error updating log level: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update log level: {str(e)}"
        )

@router.get("/logs/download")
async def download_logs(
    request: Request,
    format: str = Query("txt", description="Download format: txt or json"),
    count: int = Query(1000, ge=1, le=5000, description="Number of recent log entries"),
    level: Optional[str] = Query(None, description="Minimum log level filter")
):
    """Download application logs as a file (admin only)"""
    await verify_admin_access(request)
    
    _ensure_memory_handler()
    
    try:
        # Get logs from the memory handler
        log_entries = _memory_handler.get_recent_logs(count=count, level_filter=level)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            # JSON format
            import json
            logs_data = {
                "generated_at": datetime.utcnow().isoformat(),
                "total_entries": len(log_entries),
                "filters": {"count": count, "level": level},
                "logs": [entry.dict() for entry in log_entries]
            }
            
            content = json.dumps(logs_data, indent=2)
            filename = f"application_logs_{timestamp}.json"
            media_type = "application/json"
            
        else:
            # Plain text format
            lines = [f"Application Logs Generated: {datetime.utcnow().isoformat()}"]
            lines.append(f"Total Entries: {len(log_entries)}")
            lines.append(f"Filters: count={count}, level={level}")
            lines.append("=" * 80)
            lines.append("")
            
            for entry in log_entries:
                lines.append(f"{entry.timestamp} [{entry.level:8}] {entry.logger}: {entry.message}")
                if entry.module and entry.line_number:
                    lines.append(f"    at {entry.module}:{entry.line_number}")
                lines.append("")
            
            content = "\n".join(lines)
            filename = f"application_logs_{timestamp}.txt"
            media_type = "text/plain"
        
        # Create a file-like object
        file_obj = io.BytesIO(content.encode('utf-8'))
        
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download logs: {str(e)}"
        )

@router.post("/logs/clear")
async def clear_logs(request: Request):
    """Clear the in-memory log cache (admin only)"""
    await verify_admin_access(request)
    
    try:
        _ensure_memory_handler()
        old_count = len(_memory_handler.records)
        _memory_handler.records.clear()
        
        logger.info(f"Log cache cleared by admin (removed {old_count} entries)")
        
        return {
            "message": "Log cache cleared successfully",
            "entries_removed": old_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear logs: {str(e)}"
        )