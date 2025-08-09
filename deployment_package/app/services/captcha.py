"""
Math CAPTCHA verification service
"""

import random
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class MathCaptchaService:
    """Service for Math CAPTCHA generation and verification"""
    
    def __init__(self):
        self.min_num = 1
        self.max_num = 20
        
    def generate_math_question(self) -> Tuple[str, int]:
        """Generate a random math question and return the question string and correct answer"""
        num1 = random.randint(self.min_num, self.max_num)
        num2 = random.randint(self.min_num, self.max_num)
        
        question = f"What is {num1} + {num2}?"
        correct_answer = num1 + num2
        
        logger.debug(f"Generated math question: {question}, answer: {correct_answer}")
        return question, correct_answer
    
    def verify_math_answer(self, question: str, provided_answer: int) -> bool:
        """Verify that the provided answer matches the question"""
        try:
            # Extract numbers from question format "What is X + Y?"
            if not question.startswith("What is ") or not question.endswith("?"):
                logger.warning(f"Invalid question format: {question}")
                return False
                
            # Extract the math expression
            math_part = question[8:-1]  # Remove "What is " and "?"
            
            # Split by " + " to get the numbers
            if " + " not in math_part:
                logger.warning(f"Invalid math expression: {math_part}")
                return False
                
            parts = math_part.split(" + ")
            if len(parts) != 2:
                logger.warning(f"Invalid math expression parts: {parts}")
                return False
                
            num1 = int(parts[0])
            num2 = int(parts[1])
            correct_answer = num1 + num2
            
            is_correct = provided_answer == correct_answer
            if is_correct:
                logger.info("Math captcha verification successful")
            else:
                logger.warning(f"Math captcha verification failed: expected {correct_answer}, got {provided_answer}")
                
            return is_correct
            
        except ValueError as e:
            logger.warning(f"Error parsing math question: {e}")
            return False
        except Exception as e:
            logger.error(f"Math captcha verification error: {e}")
            return False