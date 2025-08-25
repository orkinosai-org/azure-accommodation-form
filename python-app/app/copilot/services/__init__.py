"""
Copilot Agent Services

This module contains service classes for the External Collaboration Management Copilot Agent.
"""

from .agent_service import *
from .conversation_service import *
from .task_service import *
from .integration_service import *

__all__ = [
    "CopilotAgentService",
    "ConversationService", 
    "TaskService",
    "ExternalLibraryIntegrationService"
]