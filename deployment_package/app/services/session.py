"""
Session management service
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory session storage (use Redis in production)
sessions = {}

class SessionService:
    """Service for managing user sessions"""
    
    def __init__(self):
        self.session_timeout = timedelta(hours=2)  # 2 hour session timeout
    
    async def create_session(
        self, 
        session_token: str, 
        email: str, 
        client_ip: str
    ) -> Dict[str, Any]:
        """Create a new authenticated session"""
        expires_at = datetime.utcnow() + self.session_timeout
        
        session_data = {
            "email": email,
            "client_ip": client_ip,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "last_activity": datetime.utcnow()
        }
        
        sessions[session_token] = session_data
        
        logger.info(f"Session created for {email} from IP: {client_ip}")
        return session_data
    
    async def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session data if valid"""
        session = sessions.get(session_token)
        
        if not session:
            return None
        
        # Check if session has expired
        if datetime.utcnow() > session["expires_at"]:
            await self.invalidate_session(session_token)
            return None
        
        # Update last activity
        session["last_activity"] = datetime.utcnow()
        return session
    
    async def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session"""
        if session_token in sessions:
            session = sessions[session_token]
            logger.info(f"Session invalidated for {session.get('email')}")
            del sessions[session_token]
            return True
        return False
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions (call periodically)"""
        current_time = datetime.utcnow()
        expired_tokens = [
            token for token, session in sessions.items()
            if current_time > session["expires_at"]
        ]
        
        for token in expired_tokens:
            del sessions[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
    
    async def extend_session(self, session_token: str) -> bool:
        """Extend session expiry time"""
        session = sessions.get(session_token)
        if session:
            session["expires_at"] = datetime.utcnow() + self.session_timeout
            session["last_activity"] = datetime.utcnow()
            return True
        return False
    
    async def list_active_sessions(self) -> Dict[str, Any]:
        """List all active sessions (admin only)"""
        active_sessions = []
        current_time = datetime.utcnow()
        
        for token, session in sessions.items():
            if current_time <= session["expires_at"]:
                active_sessions.append({
                    "token": token[:8] + "...",  # Truncated for security
                    "email": session["email"],
                    "client_ip": session["client_ip"],
                    "created_at": session["created_at"],
                    "last_activity": session["last_activity"],
                    "expires_at": session["expires_at"]
                })
        
        return {
            "total_sessions": len(active_sessions),
            "sessions": active_sessions
        }