"""
API test for math captcha endpoints
"""

import json
import pytest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple API test by calling the endpoints directly
def test_api_generate_math_captcha():
    """Test the API endpoint for generating math captcha"""
    from main_simple import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test the endpoint
    response = client.get("/api/auth/generate-math-captcha")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "question" in data
    assert "timestamp" in data
    
    # Validate question format
    question = data["question"]
    assert question.startswith("What is ")
    assert question.endswith("?")
    assert " + " in question


def test_api_request_email_verification():
    """Test the API endpoint for email verification with math captcha"""
    from main_simple import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # First get a math question
    captcha_response = client.get("/api/auth/generate-math-captcha")
    assert captcha_response.status_code == 200
    
    question = captcha_response.json()["question"]
    
    # Calculate the correct answer
    # Extract numbers from "What is X + Y?"
    math_part = question[8:-1]  # Remove "What is " and "?"
    num1, num2 = map(int, math_part.split(" + "))
    correct_answer = num1 + num2
    
    # Test with correct answer
    email_data = {
        "email": "test@example.com",
        "email_confirm": "test@example.com",
        "math_question": question,
        "math_answer": correct_answer
    }
    
    response = client.post("/api/auth/request-email-verification", json=email_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "verification_id" in data
    assert "message" in data
    assert "expires_at" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])