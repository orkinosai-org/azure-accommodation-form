"""
Authentication and security routes
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from app.core.security import (
    get_current_ip, 
    generate_mfa_token, 
    require_certificate_auth,
    generate_session_id
)
from app.core.config import get_settings
from app.models.form import (
    EmailVerificationRequest, 
    EmailVerificationResponse,
    MFATokenRequest,
    MFATokenResponse
)
from app.services.email import EmailService
from app.services.captcha import MathCaptchaService
from app.services.session import SessionService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory storage for verification sessions (use Redis in production)
verification_sessions = {}

@router.post("/verify-certificate")
async def verify_certificate(request: Request):
    """Verify client certificate authentication"""
    try:
        require_certificate_auth(request)
        client_ip = get_current_ip(request)
        
        logger.info(f"Certificate verification successful for IP: {client_ip}")
        
        return {
            "status": "verified",
            "message": "Certificate authentication successful",
            "client_ip": client_ip,
            "timestamp": datetime.utcnow()
        }
    except HTTPException as e:
        logger.warning(f"Certificate verification failed for IP: {get_current_ip(request)}")
        raise e

@router.get("/generate-math-captcha")
async def generate_math_captcha():
    """Generate a new math captcha question"""
    math_captcha_service = MathCaptchaService()
    question, answer = math_captcha_service.generate_math_question()
    
    # Return only the question to frontend, keep answer server-side for later verification
    return {
        "question": question,
        "timestamp": datetime.utcnow()
    }

@router.post("/request-email-verification", response_model=EmailVerificationResponse)
async def request_email_verification(
    request: EmailVerificationRequest,
    http_request: Request
):
    """Request email verification with Math CAPTCHA and MFA token"""
    
    # Validate certificate first
    require_certificate_auth(http_request)
    
    # Verify Math CAPTCHA
    math_captcha_service = MathCaptchaService()
    if not math_captcha_service.verify_math_answer(request.math_question, request.math_answer):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security verification failed. Please try again."
        )
    
    # Verify email confirmation matches
    if request.email != request.email_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email confirmation does not match"
        )
    
    # Generate verification session
    verification_id = generate_session_id()
    mfa_token = generate_mfa_token()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.mfa_token_expiry_minutes)
    
    # Store verification session
    verification_sessions[verification_id] = {
        "email": request.email,
        "mfa_token": mfa_token,
        "expires_at": expires_at,
        "verified": False,
        "client_ip": get_current_ip(http_request),
        "attempts": 0
    }
    
    # Send MFA token via email
    email_service = EmailService()
    try:
        await email_service.send_mfa_token(request.email, mfa_token)
        logger.info(f"MFA token sent to {request.email}")
    except Exception as e:
        logger.error(f"Failed to send MFA token to {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return EmailVerificationResponse(
        verification_id=verification_id,
        message=f"Verification code sent to {request.email}",
        expires_at=expires_at
    )

@router.post("/verify-mfa-token", response_model=MFATokenResponse)
async def verify_mfa_token(
    request: MFATokenRequest,
    http_request: Request
):
    """Verify MFA token and complete email verification"""
    
    # Validate certificate first
    require_certificate_auth(http_request)
    
    # Get verification session
    session = verification_sessions.get(request.verification_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification session not found"
        )
    
    # Check if session has expired
    if datetime.utcnow() > session["expires_at"]:
        del verification_sessions[request.verification_id]
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Verification session has expired"
        )
    
    # Check attempt limits
    session["attempts"] += 1
    if session["attempts"] > 5:
        del verification_sessions[request.verification_id]
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification attempts"
        )
    
    # Verify MFA token
    if request.token != session["mfa_token"]:
        logger.warning(f"Invalid MFA token attempt for verification ID: {request.verification_id}")
        return MFATokenResponse(
            verified=False,
            message="Invalid verification code"
        )
    
    # Mark session as verified
    session["verified"] = True
    session_token = generate_session_id()
    
    # Create authenticated session
    session_service = SessionService()
    await session_service.create_session(
        session_token,
        session["email"],
        get_current_ip(http_request)
    )
    
    logger.info(f"Email verification completed for {session['email']}")
    
    return MFATokenResponse(
        verified=True,
        message="Email verification successful",
        session_token=session_token
    )

@router.get("/session/status")
async def session_status(request: Request):
    """Check current session status"""
    session_token = request.headers.get("X-Session-Token")
    if not session_token:
        return {"authenticated": False}
    
    session_service = SessionService()
    session = await session_service.get_session(session_token)
    
    if not session:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "email": session.get("email"),
        "expires_at": session.get("expires_at")
    }

@router.post("/logout")
async def logout(request: Request):
    """Logout and invalidate session"""
    session_token = request.headers.get("X-Session-Token")
    if session_token:
        session_service = SessionService()
        await session_service.invalidate_session(session_token)
    
    return {"message": "Logged out successfully"}