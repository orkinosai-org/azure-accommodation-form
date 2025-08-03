"""
CAPTCHA verification service
"""

import aiohttp
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class CaptchaService:
    """Service for CAPTCHA verification"""
    
    def __init__(self):
        self.provider = settings.captcha_provider
        self.secret_key = settings.captcha_secret_key
        
    async def verify_captcha(self, token: str) -> bool:
        """Verify CAPTCHA token"""
        if not token:
            return False
            
        if self.provider == "recaptcha":
            return await self._verify_recaptcha(token)
        elif self.provider == "hcaptcha":
            return await self._verify_hcaptcha(token)
        else:
            # For development/testing, allow bypass if no provider configured
            if settings.environment == "development":
                logger.warning("CAPTCHA verification bypassed in development mode")
                return True
            return False
    
    async def _verify_recaptcha(self, token: str) -> bool:
        """Verify Google reCAPTCHA token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'secret': self.secret_key,
                    'response': token
                }
                
                async with session.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data=data
                ) as response:
                    result = await response.json()
                    
                    if result.get('success'):
                        logger.info("reCAPTCHA verification successful")
                        return True
                    else:
                        logger.warning(f"reCAPTCHA verification failed: {result.get('error-codes')}")
                        return False
                        
        except Exception as e:
            logger.error(f"reCAPTCHA verification error: {e}")
            return False
    
    async def _verify_hcaptcha(self, token: str) -> bool:
        """Verify hCaptcha token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'secret': self.secret_key,
                    'response': token
                }
                
                async with session.post(
                    'https://hcaptcha.com/siteverify',
                    data=data
                ) as response:
                    result = await response.json()
                    
                    if result.get('success'):
                        logger.info("hCaptcha verification successful")
                        return True
                    else:
                        logger.warning(f"hCaptcha verification failed: {result.get('error-codes')}")
                        return False
                        
        except Exception as e:
            logger.error(f"hCaptcha verification error: {e}")
            return False