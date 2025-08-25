"""
Admin routes for external library management
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse

from app.core.security import get_current_ip, require_certificate_auth
from app.core.config import get_settings
from app.models.external_library import (
    ExternalLibrary,
    ExternalLibraryCreate,
    ExternalLibraryUpdate,
    ExternalLibraryList,
    ExternalLibraryStats,
    ExternalUser,
    LibraryStatus
)
from app.services.external_library import ExternalLibraryService

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


# Admin authentication (reuse from admin.py)
async def verify_admin_access(request: Request):
    """Verify admin access (placeholder implementation)"""
    require_certificate_auth(request)
    
    # In production, implement proper admin authentication
    import os
    admin_token = request.headers.get("X-Admin-Token")
    
    if not admin_token or admin_token != os.getenv("ADMIN_TOKEN", "admin-secret"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def get_admin_user(request: Request) -> str:
    """Extract admin user identifier from request"""
    # In production, extract from authentication token
    return request.headers.get("X-Admin-User", "admin")


@router.get("/libraries", response_model=ExternalLibraryList)
async def list_external_libraries(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status (active/deleted)"),
    include_deleted: bool = Query(False, description="Include deleted libraries"),
    search: Optional[str] = Query(None, description="Search query")
):
    """List external libraries (admin only)"""
    await verify_admin_access(request)
    
    library_service = ExternalLibraryService()
    
    if search:
        # Return search results without pagination for now
        libraries = await library_service.search_libraries(search, include_deleted)
        return ExternalLibraryList(
            libraries=libraries,
            total=len(libraries),
            page=1,
            limit=len(libraries),
            total_pages=1
        )
    
    libraries = await library_service.list_libraries(
        page=page,
        limit=limit,
        status_filter=status_filter,
        include_deleted=include_deleted
    )
    
    return libraries


@router.get("/libraries/active", response_model=List[ExternalLibrary])
async def get_active_libraries(request: Request):
    """Get all active libraries for frontend use (admin only)"""
    await verify_admin_access(request)
    
    library_service = ExternalLibraryService()
    libraries = await library_service.get_active_libraries()
    
    return libraries


@router.get("/libraries/stats", response_model=ExternalLibraryStats)
async def get_library_statistics(request: Request):
    """Get external library statistics (admin only)"""
    await verify_admin_access(request)
    
    library_service = ExternalLibraryService()
    stats = await library_service.get_statistics()
    
    return stats


@router.post("/libraries", response_model=ExternalLibrary, status_code=status.HTTP_201_CREATED)
async def create_external_library(
    library_data: ExternalLibraryCreate,
    request: Request
):
    """Create a new external library (admin only)"""
    await verify_admin_access(request)
    admin_user = get_admin_user(request)
    
    library_service = ExternalLibraryService()
    
    try:
        library = await library_service.create_library(library_data, admin_user)
        logger.info(f"External library created: {library.id} - {library.name} by {admin_user}")
        return library
    except Exception as e:
        logger.error(f"Error creating external library: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create library: {str(e)}"
        )


@router.get("/libraries/{library_id}", response_model=ExternalLibrary)
async def get_external_library(
    library_id: str,
    request: Request
):
    """Get a specific external library (admin only)"""
    await verify_admin_access(request)
    
    library_service = ExternalLibraryService()
    library = await library_service.get_library(library_id)
    
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    return library


@router.put("/libraries/{library_id}", response_model=ExternalLibrary)
async def update_external_library(
    library_id: str,
    library_data: ExternalLibraryUpdate,
    request: Request
):
    """Update an external library (admin only)"""
    await verify_admin_access(request)
    admin_user = get_admin_user(request)
    
    library_service = ExternalLibraryService()
    
    library = await library_service.update_library(library_id, library_data, admin_user)
    
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    logger.info(f"External library updated: {library_id} - {library.name} by {admin_user}")
    return library


@router.delete("/libraries/{library_id}")
async def delete_external_library(
    library_id: str,
    request: Request,
    hard_delete: bool = Query(False, description="Permanently delete (hard delete)")
):
    """Delete an external library (admin only)"""
    await verify_admin_access(request)
    admin_user = get_admin_user(request)
    
    library_service = ExternalLibraryService()
    
    if hard_delete:
        success = await library_service.hard_delete_library(library_id, admin_user)
        action = "permanently deleted"
    else:
        success = await library_service.delete_library(library_id, admin_user)
        action = "soft deleted"
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    logger.info(f"External library {action}: {library_id} by {admin_user}")
    
    return {"message": f"Library {action} successfully"}


@router.post("/libraries/{library_id}/restore", response_model=ExternalLibrary)
async def restore_external_library(
    library_id: str,
    request: Request
):
    """Restore a soft-deleted external library (admin only)"""
    await verify_admin_access(request)
    admin_user = get_admin_user(request)
    
    library_service = ExternalLibraryService()
    library = await library_service.restore_library(library_id, admin_user)
    
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    logger.info(f"External library restored: {library_id} - {library.name} by {admin_user}")
    return library


@router.get("/libraries/{library_id}/test-connection")
async def test_library_connection(
    library_id: str,
    request: Request
):
    """Test connection to an external library (admin only)"""
    await verify_admin_access(request)
    
    library_service = ExternalLibraryService()
    library = await library_service.get_library(library_id)
    
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    # Test connection to library URL
    import aiohttp
    import asyncio
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(str(library.url), timeout=aiohttp.ClientTimeout(total=10)) as response:
                connection_status = "success" if response.status < 400 else "failed"
                status_code = response.status
    except asyncio.TimeoutError:
        connection_status = "timeout"
        status_code = None
    except Exception as e:
        connection_status = "error"
        status_code = None
        logger.error(f"Error testing library connection {library_id}: {e}")
    
    return {
        "library_id": library_id,
        "library_name": library.name,
        "url": str(library.url),
        "connection_status": connection_status,
        "status_code": status_code,
        "tested_at": library_service.__class__.__module__  # Using current time placeholder
    }


# Public endpoint for frontend to get active libraries (no admin required)
@router.get("/public/active-libraries", response_model=List[ExternalLibrary])
async def get_public_active_libraries():
    """Get active libraries for public/frontend use (no authentication required)"""
    library_service = ExternalLibraryService()
    libraries = await library_service.get_active_libraries()
    
    # Return only essential fields for frontend
    return [
        {
            "id": lib.id,
            "name": lib.name,
            "url": str(lib.url),
            "description": lib.description,
            "external_users": lib.external_users
        }
        for lib in libraries
    ]


# External User Management Endpoints for Web Parts
@router.post("/libraries/{library_id}/external-users")
async def add_external_user_to_library(
    library_id: str,
    user_data: ExternalUser,
    request: Request
):
    """Add an external user to a library (admin only)"""
    await verify_admin_access(request)
    admin_user = get_admin_user(request)
    
    library_service = ExternalLibraryService()
    library = await library_service.get_library(library_id)
    
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    # Check if user already exists in the library
    for existing_user in library.external_users:
        if existing_user.email.lower() == user_data.email.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {user_data.email} already has access to this library"
            )
    
    # Add the new user to the library
    updated_users = library.external_users + [user_data]
    update_data = ExternalLibraryUpdate(external_users=updated_users)
    
    updated_library = await library_service.update_library(library_id, update_data, admin_user)
    
    logger.info(f"External user {user_data.email} added to library {library_id} by {admin_user}")
    
    return {
        "message": f"User {user_data.email} added to library successfully",
        "library_id": library_id,
        "user": user_data,
        "total_users": len(updated_library.external_users)
    }


@router.delete("/libraries/{library_id}/external-users/{user_email}")
async def remove_external_user_from_library(
    library_id: str,
    user_email: str,
    request: Request
):
    """Remove an external user from a library (admin only)"""
    await verify_admin_access(request)
    admin_user = get_admin_user(request)
    
    library_service = ExternalLibraryService()
    library = await library_service.get_library(library_id)
    
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    # Find and remove the user
    user_email_lower = user_email.lower()
    original_count = len(library.external_users)
    updated_users = [
        user for user in library.external_users 
        if user.email.lower() != user_email_lower
    ]
    
    if len(updated_users) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_email} not found in library"
        )
    
    # Update the library
    update_data = ExternalLibraryUpdate(external_users=updated_users)
    updated_library = await library_service.update_library(library_id, update_data, admin_user)
    
    logger.info(f"External user {user_email} removed from library {library_id} by {admin_user}")
    
    return {
        "message": f"User {user_email} removed from library successfully",
        "library_id": library_id,
        "removed_user_email": user_email,
        "total_users": len(updated_library.external_users)
    }


@router.get("/libraries/{library_id}/external-users", response_model=List[ExternalUser])
async def get_library_external_users(
    library_id: str,
    request: Request
):
    """Get external users for a specific library (admin only)"""
    await verify_admin_access(request)
    
    library_service = ExternalLibraryService()
    library = await library_service.get_library(library_id)
    
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External library not found"
        )
    
    return library.external_users


@router.post("/libraries/{library_id}/external-users/check-access")
async def check_user_access_to_library(
    library_id: str,
    user_email: str = Body(..., embed=True),
    request: Request = None
):
    """Check if a user has access to a specific library (public endpoint)"""
    library_service = ExternalLibraryService()
    library = await library_service.get_library(library_id)
    
    if not library or library.status != LibraryStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active library not found"
        )
    
    # Check if user has access
    user_email_lower = user_email.lower()
    has_access = any(
        user.email.lower() == user_email_lower 
        for user in library.external_users
    )
    
    user_details = None
    if has_access:
        user_details = next(
            user for user in library.external_users 
            if user.email.lower() == user_email_lower
        )
    
    return {
        "library_id": library_id,
        "library_name": library.name,
        "user_email": user_email,
        "has_access": has_access,
        "user_details": user_details,
        "total_external_users": len(library.external_users)
    }