"""
Agent models for the Copilot agent
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

from .conversation import ConversationMessage
from .task import Task


class AgentCapability(str, Enum):
    """Capabilities of the Copilot agent"""
    EXTERNAL_LIBRARY_MANAGEMENT = "external_library_management"
    USER_ACCESS_CONTROL = "user_access_control"
    SHAREPOINT_INTEGRATION = "sharepoint_integration"
    CONVERSATION_MANAGEMENT = "conversation_management"
    TASK_AUTOMATION = "task_automation"
    REPORTING_ANALYTICS = "reporting_analytics"
    HELP_DOCUMENTATION = "help_documentation"


class AgentResponseType(str, Enum):
    """Type of agent response"""
    TEXT = "text"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    ERROR = "error"
    HELP = "help"


class AgentAction(BaseModel):
    """Action that the agent can perform"""
    action_type: str = Field(..., description="Type of action")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    description: str = Field(..., description="Human-readable description of the action")
    requires_confirmation: bool = Field(default=False, description="Whether action requires user confirmation")


class AgentResponse(BaseModel):
    """Response from the Copilot agent"""
    response_type: AgentResponseType = Field(..., description="Type of response")
    content: str = Field(..., description="Response content")
    actions: List[AgentAction] = Field(default_factory=list, description="Actions suggested or performed")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    context_updates: Optional[Dict[str, Any]] = Field(None, description="Updates to conversation context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    
    # Task information if response relates to a task
    task_id: Optional[str] = Field(None, description="Associated task ID")
    task_status: Optional[str] = Field(None, description="Current task status")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class AgentContext(BaseModel):
    """Context for agent operations"""
    user_id: Optional[str] = Field(None, description="Current user ID")
    session_id: str = Field(..., description="Current session ID")
    
    # External library context
    current_libraries: List[str] = Field(default_factory=list, description="Currently relevant library IDs")
    user_permissions: Dict[str, List[str]] = Field(default_factory=dict, description="User permissions by library")
    
    # Conversation context
    recent_topics: List[str] = Field(default_factory=list, description="Recent conversation topics")
    pending_confirmations: List[str] = Field(default_factory=list, description="Pending user confirmations")
    
    # System context
    capabilities_enabled: List[AgentCapability] = Field(default_factory=list, description="Enabled capabilities")
    system_status: Dict[str, Any] = Field(default_factory=dict, description="System status information")
    
    # User preferences
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences and settings")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Context creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class AgentIntent(BaseModel):
    """Detected user intent"""
    intent_type: str = Field(..., description="Type of detected intent")
    confidence: float = Field(..., description="Confidence score (0-1)")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Intent parameters")


class AgentRequest(BaseModel):
    """Request to the Copilot agent"""
    user_message: str = Field(..., description="User's message")
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    context: Optional[AgentContext] = Field(None, description="Current context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional request metadata")