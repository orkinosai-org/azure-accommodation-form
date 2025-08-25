"""
Copilot Agent Models

This module contains Pydantic models for the External Collaboration Management Copilot Agent.
"""

from .conversation import *
from .task import *
from .agent import *

__all__ = [
    "ConversationMessage",
    "ConversationSession", 
    "ConversationCreate",
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskStatus",
    "AgentCapability",
    "AgentResponse",
    "AgentContext"
]