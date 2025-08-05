"""
Integration test for math captcha functionality 
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.captcha import MathCaptchaService
from app.models.form import EmailVerificationRequest


def test_math_captcha_service_integration():
    """Test math captcha service integration with models"""
    service = MathCaptchaService()
    
    # Generate a math question
    question, correct_answer = service.generate_math_question()
    
    # Create a request model with correct answer
    request = EmailVerificationRequest(
        email="test@example.com",
        email_confirm="test@example.com",
        math_question=question,
        math_answer=correct_answer
    )
    
    # Verify the answer
    result = service.verify_math_answer(request.math_question, request.math_answer)
    assert result is True
    
    # Test with wrong answer
    request.math_answer = correct_answer + 1
    result = service.verify_math_answer(request.math_question, request.math_answer)
    assert result is False


def test_email_verification_request_validation():
    """Test that EmailVerificationRequest properly validates math captcha fields"""
    # Test valid request
    question = "What is 5 + 7?"
    answer = 12
    
    request = EmailVerificationRequest(
        email="test@example.com",
        email_confirm="test@example.com", 
        math_question=question,
        math_answer=answer
    )
    
    assert request.email == "test@example.com"
    assert request.email_confirm == "test@example.com"
    assert request.math_question == question
    assert request.math_answer == answer


def test_math_captcha_workflow():
    """Test the complete math captcha workflow"""
    service = MathCaptchaService()
    
    # Step 1: Generate question (simulates GET /api/auth/generate-math-captcha)
    question, expected_answer = service.generate_math_question()
    
    # Step 2: User submits form with answer (simulates POST /api/auth/request-email-verification)
    user_answer = expected_answer  # User provides correct answer
    
    # Step 3: Server validates answer
    is_valid = service.verify_math_answer(question, user_answer)
    assert is_valid is True
    
    # Test with wrong answer
    wrong_answer = expected_answer + 5
    is_valid = service.verify_math_answer(question, wrong_answer)
    assert is_valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])