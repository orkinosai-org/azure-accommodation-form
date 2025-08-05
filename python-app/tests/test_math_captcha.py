"""
Test math captcha functionality
"""

import pytest
from app.services.captcha import MathCaptchaService


def test_math_captcha_service_generation():
    """Test that math captcha service generates valid questions"""
    service = MathCaptchaService()
    
    question, answer = service.generate_math_question()
    
    # Check question format
    assert question.startswith("What is ")
    assert question.endswith("?")
    assert " + " in question
    
    # Check answer is a reasonable number (2-40 based on 1-20 + 1-20)
    assert isinstance(answer, int)
    assert 2 <= answer <= 40


def test_math_captcha_verification_correct():
    """Test verification with correct answer"""
    service = MathCaptchaService()
    
    # Test with a known question and answer
    question = "What is 5 + 7?"
    correct_answer = 12
    
    result = service.verify_math_answer(question, correct_answer)
    assert result is True


def test_math_captcha_verification_incorrect():
    """Test verification with incorrect answer"""
    service = MathCaptchaService()
    
    # Test with a known question and wrong answer
    question = "What is 5 + 7?"
    wrong_answer = 10
    
    result = service.verify_math_answer(question, wrong_answer)
    assert result is False


def test_math_captcha_verification_invalid_format():
    """Test verification with invalid question format"""
    service = MathCaptchaService()
    
    # Test with invalid question formats
    invalid_questions = [
        "5 + 7",
        "What is 5 - 7?",
        "What is 5 + 7",
        "What are 5 + 7?",
        "What is 5 * 7?",
        ""
    ]
    
    for invalid_question in invalid_questions:
        result = service.verify_math_answer(invalid_question, 12)
        assert result is False


def test_math_captcha_verification_non_numeric():
    """Test verification with non-numeric parts"""
    service = MathCaptchaService()
    
    # Test with non-numeric question
    question = "What is five + seven?"
    result = service.verify_math_answer(question, 12)
    assert result is False


def test_multiple_generations_are_different():
    """Test that multiple generations produce different questions"""
    service = MathCaptchaService()
    
    questions = []
    answers = []
    
    # Generate 10 questions
    for _ in range(10):
        question, answer = service.generate_math_question()
        questions.append(question)
        answers.append(answer)
    
    # Check that we got variety (at least 5 different questions out of 10)
    unique_questions = set(questions)
    assert len(unique_questions) >= 5, "Should generate varied questions"