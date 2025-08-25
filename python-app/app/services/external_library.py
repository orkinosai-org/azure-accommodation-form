"""
External Library management service
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.external_library import (
    ExternalLibrary, 
    ExternalLibraryCreate, 
    ExternalLibraryUpdate, 
    ExternalLibraryList,
    ExternalLibraryStats,
    LibraryStatus
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory storage for external libraries (use database in production)
external_libraries = {}


class ExternalLibraryService:
    """Service for managing external libraries"""
    
    def __init__(self):
        self._initialize_default_libraries()
    
    def _initialize_default_libraries(self):
        """Initialize with some default libraries if none exist"""
        if not external_libraries:
            # Add a sample library
            sample_library = ExternalLibrary(
                id="sample-lib-001",
                name="Sample Document Library",
                url="https://example.sharepoint.com/sites/sample/Shared%20Documents",
                description="Sample external document library for demonstration",
                external_users=[],
                status=LibraryStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by="system",
                updated_by="system"
            )
            external_libraries[sample_library.id] = sample_library.dict()
            logger.info("Initialized default external libraries")
    
    async def create_library(self, library_data: ExternalLibraryCreate, admin_user: str = "admin") -> ExternalLibrary:
        """Create a new external library"""
        library_id = str(uuid.uuid4())
        
        library = ExternalLibrary(
            id=library_id,
            name=library_data.name,
            url=library_data.url,
            description=library_data.description,
            external_users=library_data.external_users,
            status=LibraryStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=admin_user,
            updated_by=admin_user
        )
        
        external_libraries[library_id] = library.dict()
        logger.info(f"External library created: {library_id} - {library.name} by {admin_user}")
        
        return library
    
    async def get_library(self, library_id: str) -> Optional[ExternalLibrary]:
        """Get a specific external library by ID"""
        library_data = external_libraries.get(library_id)
        if library_data:
            return ExternalLibrary(**library_data)
        return None
    
    async def list_libraries(
        self, 
        page: int = 1, 
        limit: int = 50, 
        status_filter: Optional[str] = None,
        include_deleted: bool = False
    ) -> ExternalLibraryList:
        """List external libraries with pagination and filtering"""
        
        # Filter libraries
        filtered_libraries = []
        for lib_data in external_libraries.values():
            library = ExternalLibrary(**lib_data)
            
            # Apply status filter
            if not include_deleted and library.status == LibraryStatus.DELETED:
                continue
            
            if status_filter and library.status != status_filter:
                continue
                
            filtered_libraries.append(library)
        
        # Sort by created_at (newest first)
        filtered_libraries.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        total = len(filtered_libraries)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_libraries = filtered_libraries[start_idx:end_idx]
        
        total_pages = (total + limit - 1) // limit
        
        return ExternalLibraryList(
            libraries=paginated_libraries,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    async def update_library(
        self, 
        library_id: str, 
        library_data: ExternalLibraryUpdate, 
        admin_user: str = "admin"
    ) -> Optional[ExternalLibrary]:
        """Update an external library"""
        if library_id not in external_libraries:
            return None
        
        current_library = ExternalLibrary(**external_libraries[library_id])
        
        # Update only provided fields
        update_data = library_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_library, field):
                setattr(current_library, field, value)
        
        # Update metadata
        current_library.updated_at = datetime.utcnow()
        current_library.updated_by = admin_user
        
        external_libraries[library_id] = current_library.dict()
        logger.info(f"External library updated: {library_id} - {current_library.name} by {admin_user}")
        
        return current_library
    
    async def delete_library(self, library_id: str, admin_user: str = "admin") -> bool:
        """Soft delete an external library (mark as deleted)"""
        if library_id not in external_libraries:
            return False
        
        library_data = external_libraries[library_id]
        library = ExternalLibrary(**library_data)
        
        # Mark as deleted instead of removing
        library.status = LibraryStatus.DELETED
        library.updated_at = datetime.utcnow()
        library.updated_by = admin_user
        
        external_libraries[library_id] = library.dict()
        logger.info(f"External library soft deleted: {library_id} - {library.name} by {admin_user}")
        
        return True
    
    async def restore_library(self, library_id: str, admin_user: str = "admin") -> Optional[ExternalLibrary]:
        """Restore a soft-deleted external library"""
        if library_id not in external_libraries:
            return None
        
        library_data = external_libraries[library_id]
        library = ExternalLibrary(**library_data)
        
        if library.status != LibraryStatus.DELETED:
            return library  # Already active
        
        # Restore library
        library.status = LibraryStatus.ACTIVE
        library.updated_at = datetime.utcnow()
        library.updated_by = admin_user
        
        external_libraries[library_id] = library.dict()
        logger.info(f"External library restored: {library_id} - {library.name} by {admin_user}")
        
        return library
    
    async def hard_delete_library(self, library_id: str, admin_user: str = "admin") -> bool:
        """Permanently delete an external library (remove from storage)"""
        if library_id not in external_libraries:
            return False
        
        library_data = external_libraries[library_id]
        library = ExternalLibrary(**library_data)
        
        del external_libraries[library_id]
        logger.warning(f"External library permanently deleted: {library_id} - {library.name} by {admin_user}")
        
        return True
    
    async def get_active_libraries(self) -> List[ExternalLibrary]:
        """Get all active libraries for frontend consumption"""
        active_libraries = []
        
        for lib_data in external_libraries.values():
            library = ExternalLibrary(**lib_data)
            if library.status == LibraryStatus.ACTIVE:
                active_libraries.append(library)
        
        # Sort by name
        active_libraries.sort(key=lambda x: x.name.lower())
        
        return active_libraries
    
    async def get_statistics(self) -> ExternalLibraryStats:
        """Get statistics about external libraries"""
        total_libraries = len(external_libraries)
        active_count = 0
        deleted_count = 0
        total_users = set()
        
        recent_activity = []
        
        for lib_data in external_libraries.values():
            library = ExternalLibrary(**lib_data)
            
            if library.status == LibraryStatus.ACTIVE:
                active_count += 1
            elif library.status == LibraryStatus.DELETED:
                deleted_count += 1
            
            # Count unique external users
            for user in library.external_users:
                total_users.add(user.email)
            
            # Add to recent activity
            recent_activity.append({
                "library_id": library.id,
                "library_name": library.name,
                "action": "updated" if library.updated_at > library.created_at else "created",
                "timestamp": library.updated_at,
                "admin_user": library.updated_by or library.created_by
            })
        
        # Sort recent activity by timestamp (newest first) and limit to 10
        recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activity = recent_activity[:10]
        
        libraries_by_status = {
            "active": active_count,
            "deleted": deleted_count
        }
        
        return ExternalLibraryStats(
            total_libraries=total_libraries,
            active_libraries=active_count,
            deleted_libraries=deleted_count,
            total_external_users=len(total_users),
            libraries_by_status=libraries_by_status,
            recent_activity=recent_activity
        )
    
    async def search_libraries(self, query: str, include_deleted: bool = False) -> List[ExternalLibrary]:
        """Search libraries by name or description"""
        query_lower = query.lower()
        matching_libraries = []
        
        for lib_data in external_libraries.values():
            library = ExternalLibrary(**lib_data)
            
            # Skip deleted libraries unless requested
            if not include_deleted and library.status == LibraryStatus.DELETED:
                continue
            
            # Search in name and description
            if (query_lower in library.name.lower() or 
                (library.description and query_lower in library.description.lower())):
                matching_libraries.append(library)
        
        # Sort by relevance (name matches first, then description matches)
        matching_libraries.sort(key=lambda x: (
            query_lower not in x.name.lower(),  # Name matches first
            x.name.lower()
        ))
        
        return matching_libraries