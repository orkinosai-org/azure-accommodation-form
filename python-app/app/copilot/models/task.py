"""
Task models for the Copilot agent
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Type of task"""
    LIBRARY_MANAGEMENT = "library_management"
    USER_ACCESS = "user_access"
    EXTERNAL_COLLABORATION = "external_collaboration"
    INFORMATION_RETRIEVAL = "information_retrieval"
    REPORTING = "reporting"


class TaskPriority(str, Enum):
    """Priority level of a task"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    """Task model for Copilot agent operations"""
    id: str = Field(..., description="Task unique identifier")
    conversation_id: Optional[str] = Field(None, description="Associated conversation ID")
    user_id: Optional[str] = Field(None, description="User who requested the task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    task_type: TaskType = Field(..., description="Type of task")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    
    # Task parameters and results
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Task input parameters")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task execution result")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    
    # Execution details
    execution_steps: List[str] = Field(default_factory=list, description="Steps taken during execution")
    progress: float = Field(default=0.0, description="Task progress percentage (0-100)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TaskCreate(BaseModel):
    """Model for creating a new task"""
    conversation_id: Optional[str] = Field(None, description="Associated conversation ID")
    user_id: Optional[str] = Field(None, description="User requesting the task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    task_type: TaskType = Field(..., description="Type of task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Task input parameters")


class TaskUpdate(BaseModel):
    """Model for updating a task"""
    title: Optional[str] = Field(None, description="Updated task title")
    description: Optional[str] = Field(None, description="Updated task description")
    status: Optional[TaskStatus] = Field(None, description="Updated task status")
    priority: Optional[TaskPriority] = Field(None, description="Updated task priority")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    progress: Optional[float] = Field(None, description="Updated progress percentage")
    execution_steps: Optional[List[str]] = Field(None, description="Updated execution steps")