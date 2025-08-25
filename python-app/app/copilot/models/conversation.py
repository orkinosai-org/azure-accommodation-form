"""
Conversation models for the Copilot agent
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Role of the message sender"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Type of message content"""
    TEXT = "text"
    ACTION = "action"
    RESULT = "result"
    ERROR = "error"


class ConversationMessage(BaseModel):
    """Individual message in a conversation"""
    id: str = Field(..., description="Message unique identifier")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ConversationSession(BaseModel):
    """Conversation session with the Copilot agent"""
    id: str = Field(..., description="Session unique identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    title: Optional[str] = Field(None, description="Conversation title")
    messages: List[ConversationMessage] = Field(default_factory=list, description="Messages in conversation")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Session context and state")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    is_active: bool = Field(default=True, description="Whether session is active")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ConversationCreate(BaseModel):
    """Model for creating a new conversation"""
    user_id: Optional[str] = Field(None, description="User identifier")
    title: Optional[str] = Field(None, description="Initial conversation title")
    initial_message: Optional[str] = Field(None, description="Initial user message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Initial context")


class MessageCreate(BaseModel):
    """Model for creating a new message"""
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")