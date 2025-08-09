"""
Security utilities and authentication helpers
"""

import secrets
import hashlib
import hmac
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_current_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded IP first (behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"

def generate_mfa_token() -> str:
    """Generate a random MFA token"""
    token_length = settings.mfa_token_length
    return ''.join(secrets.choice('0123456789') for _ in range(token_length))

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_signature(message: str, signature: str, secret: str) -> bool:
    """Verify HMAC signature"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def generate_session_id() -> str:
    """Generate a secure session ID"""
    return secrets.token_urlsafe(32)

def validate_client_certificate(request: Request) -> bool:
    """Validate client certificate (placeholder for actual implementation)"""
    # In production, this would validate the client certificate
    # For now, we'll check for a specific header or implement basic validation
    cert_header = request.headers.get("X-Client-Cert")
    
    # In development, allow all requests
    if settings.environment == "development":
        return True
    
    # In production, implement proper certificate validation
    # This is a placeholder - implement actual certificate validation logic
    return cert_header is not None

async def get_current_user(request: Request):
    """Get current authenticated user (if any)"""
    # Extract session or token from request
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return None
    
    # Validate session (implement session storage as needed)
    # For now, return a basic user object
    return {"session_id": session_id, "ip": get_current_ip(request)}

def require_certificate_auth(request: Request):
    """Require certificate-based authentication"""
    if not validate_client_certificate(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid client certificate required"
        )