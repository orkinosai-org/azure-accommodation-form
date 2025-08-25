"""
External Library Integration Service for Copilot Agent

Provides integration with the existing external library management system.
"""

import logging
from typing import List, Optional, Dict, Any

from app.services.external_library import ExternalLibraryService
from app.models.external_library import ExternalLibrary, ExternalLibraryStats

logger = logging.getLogger(__name__)


class ExternalLibraryIntegrationService:
    """
    Integration service that connects the Copilot agent with the existing
    external library management system.
    """
    
    def __init__(self):
        self.external_library_service = ExternalLibraryService()
    
    async def get_active_libraries(self) -> List[ExternalLibrary]:
        """Get all active external libraries"""
        try:
            libraries = await self.external_library_service.get_active_libraries()
            logger.info(f"Retrieved {len(libraries)} active libraries for Copilot")
            return libraries
        except Exception as e:
            logger.error(f"Error retrieving active libraries: {e}")
            return []
    
    async def get_library_by_id(self, library_id: str) -> Optional[ExternalLibrary]:
        """Get a specific library by ID"""
        try:
            library = await self.external_library_service.get_library(library_id)
            return library
        except Exception as e:
            logger.error(f"Error retrieving library {library_id}: {e}")
            return None
    
    async def get_library_statistics(self) -> ExternalLibraryStats:
        """Get statistics about external libraries"""
        try:
            stats = await self.external_library_service.get_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error retrieving library statistics: {e}")
            # Return default stats in case of error
            return ExternalLibraryStats(
                total_libraries=0,
                active_libraries=0,
                deleted_libraries=0,
                total_external_users=0,
                libraries_by_status={"active": 0, "deleted": 0},
                recent_activity=[]
            )
    
    async def search_libraries(self, query: str) -> List[ExternalLibrary]:
        """Search libraries by name or description"""
        try:
            libraries = await self.external_library_service.search_libraries(query)
            logger.info(f"Found {len(libraries)} libraries matching query: {query}")
            return libraries
        except Exception as e:
            logger.error(f"Error searching libraries with query '{query}': {e}")
            return []
    
    async def get_libraries_for_user(self, user_email: str) -> List[ExternalLibrary]:
        """Get libraries that a specific user has access to"""
        try:
            all_libraries = await self.get_active_libraries()
            user_libraries = []
            
            for library in all_libraries:
                # Check if user is in the external users list
                for external_user in library.external_users:
                    if external_user.email.lower() == user_email.lower():
                        user_libraries.append(library)
                        break
            
            logger.info(f"User {user_email} has access to {len(user_libraries)} libraries")
            return user_libraries
            
        except Exception as e:
            logger.error(f"Error retrieving libraries for user {user_email}: {e}")
            return []
    
    async def get_user_access_summary(self, user_email: str) -> Dict[str, Any]:
        """Get a summary of user's access across all libraries"""
        try:
            user_libraries = await self.get_libraries_for_user(user_email)
            
            summary = {
                "user_email": user_email,
                "total_libraries_access": len(user_libraries),
                "libraries": []
            }
            
            for library in user_libraries:
                # Find the user's details in this library
                user_details = None
                for external_user in library.external_users:
                    if external_user.email.lower() == user_email.lower():
                        user_details = external_user
                        break
                
                library_info = {
                    "library_id": library.id,
                    "library_name": library.name,
                    "library_url": str(library.url),
                    "user_name": user_details.name if user_details else "Unknown",
                    "user_organization": user_details.organization if user_details else None
                }
                summary["libraries"].append(library_info)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating user access summary for {user_email}: {e}")
            return {
                "user_email": user_email,
                "total_libraries_access": 0,
                "libraries": [],
                "error": str(e)
            }
    
    async def validate_library_access(self, library_id: str, user_email: str) -> bool:
        """Check if a user has access to a specific library"""
        try:
            library = await self.get_library_by_id(library_id)
            if not library:
                return False
            
            # Check if user is in external users list
            for external_user in library.external_users:
                if external_user.email.lower() == user_email.lower():
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating library access for user {user_email} and library {library_id}: {e}")
            return False
    
    async def get_library_users(self, library_id: str) -> List[Dict[str, Any]]:
        """Get all users who have access to a specific library"""
        try:
            library = await self.get_library_by_id(library_id)
            if not library:
                return []
            
            users = []
            for external_user in library.external_users:
                user_info = {
                    "email": external_user.email,
                    "name": external_user.name,
                    "organization": external_user.organization
                }
                users.append(user_info)
            
            logger.info(f"Library {library_id} has {len(users)} external users")
            return users
            
        except Exception as e:
            logger.error(f"Error retrieving users for library {library_id}: {e}")
            return []
    
    async def get_recent_library_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity across all libraries"""
        try:
            stats = await self.get_library_statistics()
            return stats.recent_activity[:limit]
        except Exception as e:
            logger.error(f"Error retrieving recent library activity: {e}")
            return []