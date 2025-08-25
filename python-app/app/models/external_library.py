"""
Pydantic models for external library management
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field, EmailStr
from enum import Enum


class LibraryStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class ExternalUser(BaseModel):
    """Model for external users that can access the library"""
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    organization: Optional[str] = Field(None, max_length=100, description="User's organization")


class ExternalLibraryBase(BaseModel):
    """Base model for external library data"""
    name: str = Field(..., min_length=1, max_length=200, description="Library name")
    url: HttpUrl = Field(..., description="Library URL")
    description: Optional[str] = Field(None, max_length=1000, description="Library info/description")
    external_users: List[ExternalUser] = Field(default_factory=list, description="External users with access")


class ExternalLibraryCreate(ExternalLibraryBase):
    """Model for creating a new external library"""
    pass


class ExternalLibraryUpdate(BaseModel):
    """Model for updating an external library"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Library name")
    url: Optional[HttpUrl] = Field(None, description="Library URL")
    description: Optional[str] = Field(None, max_length=1000, description="Library info/description")
    external_users: Optional[List[ExternalUser]] = Field(None, description="External users with access")
    status: Optional[LibraryStatus] = Field(None, description="Library status")


class ExternalLibrary(ExternalLibraryBase):
    """Full external library model with metadata"""
    id: str = Field(..., description="Library unique identifier")
    status: LibraryStatus = Field(default=LibraryStatus.ACTIVE, description="Library status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Admin user who created the library")
    updated_by: Optional[str] = Field(None, description="Admin user who last updated the library")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ExternalLibraryList(BaseModel):
    """Model for listing external libraries with pagination"""
    libraries: List[ExternalLibrary]
    total: int
    page: int
    limit: int
    total_pages: int


class ExternalLibraryStats(BaseModel):
    """Model for external library statistics"""
    total_libraries: int
    active_libraries: int
    deleted_libraries: int
    total_external_users: int
    libraries_by_status: dict
    recent_activity: List[dict]