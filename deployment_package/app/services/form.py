"""
Form processing service
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.form import AccommodationFormData
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory storage for form submissions (use database in production)
form_submissions = {}
form_sessions = {}

class FormService:
    """Service for processing form submissions"""
    
    def __init__(self):
        pass
    
    async def create_form_session(self, email: str, client_ip: str) -> Dict[str, Any]:
        """Create a new form session"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "id": session_id,
            "email": email,
            "client_ip": client_ip,
            "created_at": datetime.utcnow(),
            "status": "initialized"
        }
        
        form_sessions[session_id] = session_data
        logger.info(f"Form session created: {session_id} for {email}")
        
        return session_data
    
    async def process_submission(self, form_data: AccommodationFormData) -> Dict[str, Any]:
        """Process a form submission"""
        submission_id = str(uuid.uuid4())
        
        submission = {
            "id": submission_id,
            "email": form_data.tenant_details.email,
            "full_name": form_data.tenant_details.full_name,
            "client_ip": form_data.client_ip,
            "form_data": form_data.dict(),
            "status": "processing",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "pdf_filename": None,
            "blob_url": None
        }
        
        form_submissions[submission_id] = submission
        logger.info(f"Form submission created: {submission_id}")
        
        return submission
    
    async def update_submission_status(
        self,
        submission_id: str,
        status: str,
        pdf_filename: Optional[str] = None,
        blob_url: Optional[str] = None
    ) -> bool:
        """Update submission status and metadata"""
        submission = form_submissions.get(submission_id)
        if not submission:
            return False
        
        submission["status"] = status
        submission["updated_at"] = datetime.utcnow()
        
        if pdf_filename:
            submission["pdf_filename"] = pdf_filename
        
        if blob_url:
            submission["blob_url"] = blob_url
        
        logger.info(f"Submission {submission_id} status updated to: {status}")
        return True
    
    async def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission by ID"""
        return form_submissions.get(submission_id)
    
    async def get_submission_with_details(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission with full form data"""
        submission = form_submissions.get(submission_id)
        if not submission:
            return None
        
        # Return a copy with full details
        return submission.copy()
    
    async def list_submissions(
        self,
        page: int = 1,
        limit: int = 50,
        status_filter: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """List submissions with pagination and filtering"""
        
        # Filter submissions
        filtered_submissions = []
        
        for submission in form_submissions.values():
            # Status filter
            if status_filter and submission["status"] != status_filter:
                continue
            
            # Date filters
            if from_date and submission["created_at"] < from_date:
                continue
            
            if to_date and submission["created_at"] > to_date:
                continue
            
            # Create summary (without full form data for listing)
            summary = {
                "id": submission["id"],
                "email": submission["email"],
                "full_name": submission["full_name"],
                "client_ip": submission["client_ip"],
                "status": submission["status"],
                "created_at": submission["created_at"],
                "updated_at": submission["updated_at"],
                "pdf_filename": submission.get("pdf_filename")
            }
            
            filtered_submissions.append(summary)
        
        # Sort by creation date (newest first)
        filtered_submissions.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Pagination
        total = len(filtered_submissions)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        return {
            "items": filtered_submissions[start_idx:end_idx],
            "total": total,
            "page": page,
            "limit": limit
        }
    
    async def delete_submission(self, submission_id: str) -> bool:
        """Delete a submission"""
        if submission_id in form_submissions:
            del form_submissions[submission_id]
            logger.info(f"Submission deleted: {submission_id}")
            return True
        return False
    
    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get submission statistics"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_submissions = [
            sub for sub in form_submissions.values()
            if sub["created_at"] >= cutoff_date
        ]
        
        # Status counts
        status_counts = {}
        for submission in recent_submissions:
            status = submission["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Daily counts
        daily_counts = {}
        for submission in recent_submissions:
            date_key = submission["created_at"].strftime("%Y-%m-%d")
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        return {
            "period_days": days,
            "total_submissions": len(recent_submissions),
            "total_all_time": len(form_submissions),
            "status_breakdown": status_counts,
            "daily_submissions": daily_counts,
            "average_per_day": len(recent_submissions) / days if days > 0 else 0
        }
    
    async def validate_form_data(self, form_data: AccommodationFormData) -> List[str]:
        """Validate form data and return list of validation errors"""
        errors = []
        
        # Check address history covers required period
        if len(form_data.address_history) == 0:
            errors.append("At least one address in history is required")
        
        # Check current address (most recent without end date)
        current_addresses = [
            addr for addr in form_data.address_history 
            if addr.to_date is None
        ]
        
        if len(current_addresses) == 0:
            errors.append("Current address must be specified (no end date)")
        elif len(current_addresses) > 1:
            errors.append("Only one current address is allowed")
        
        # Check occupation agreement
        required_agreements = [
            form_data.occupation_agreement.single_occupancy_agree,
            form_data.occupation_agreement.hmo_terms_agree,
            form_data.occupation_agreement.no_unlisted_occupants,
            form_data.occupation_agreement.no_smoking,
            form_data.occupation_agreement.kitchen_cooking_only
        ]
        
        if not all(required_agreements):
            errors.append("All occupation agreement terms must be accepted")
        
        # Check consent and declaration
        if not form_data.consent_and_declaration.consent_given:
            errors.append("Consent must be given")
        
        declaration = form_data.consent_and_declaration.declaration
        required_declarations = [
            declaration.main_home,
            declaration.enquiries_permission,
            declaration.certify_no_judgements,
            declaration.certify_no_housing_debt,
            declaration.certify_no_landlord_debt,
            declaration.certify_no_abuse
        ]
        
        if not all(required_declarations):
            errors.append("All declaration statements must be confirmed")
        
        return errors
    
    async def get_form_sessions_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Get all form sessions for an email"""
        sessions = [
            session for session in form_sessions.values()
            if session["email"] == email
        ]
        
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)
    
    async def cleanup_old_sessions(self, days: int = 7):
        """Clean up old form sessions"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_session_ids = [
            session_id for session_id, session in form_sessions.items()
            if session["created_at"] < cutoff_date
        ]
        
        for session_id in old_session_ids:
            del form_sessions[session_id]
        
        if old_session_ids:
            logger.info(f"Cleaned up {len(old_session_ids)} old form sessions")
        
        return len(old_session_ids)