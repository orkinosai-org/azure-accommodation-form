"""
Main Copilot Agent Service

This service orchestrates the AI-powered assistant for external collaboration management.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.copilot.models.agent import (
    AgentRequest, AgentResponse, AgentResponseType, AgentAction, 
    AgentContext, AgentIntent, AgentCapability
)
from app.copilot.models.conversation import ConversationMessage, MessageRole
from app.copilot.models.task import TaskType, TaskCreate
from .conversation_service import ConversationService
from .task_service import TaskService
from .integration_service import ExternalLibraryIntegrationService

logger = logging.getLogger(__name__)


class CopilotAgentService:
    """
    Main Copilot Agent Service for External Collaboration Management
    
    This service provides AI-powered assistance for:
    - Managing external SharePoint libraries
    - Controlling user access and permissions
    - Automating collaboration tasks
    - Providing conversational interfaces
    """
    
    def __init__(self):
        self.conversation_service = ConversationService()
        self.task_service = TaskService()
        self.integration_service = ExternalLibraryIntegrationService()
        
        # Enabled capabilities
        self.capabilities = [
            AgentCapability.EXTERNAL_LIBRARY_MANAGEMENT,
            AgentCapability.USER_ACCESS_CONTROL,
            AgentCapability.CONVERSATION_MANAGEMENT,
            AgentCapability.TASK_AUTOMATION,
            AgentCapability.HELP_DOCUMENTATION
        ]
        
        # Intent patterns for simple NLP
        self.intent_patterns = {
            "library_list": ["list libraries", "show libraries", "what libraries", "available libraries", "all libraries", "external libraries"],
            "library_create": ["create library", "add library", "new library", "create a new", "help me create"],
            "library_update": ["update library", "edit library", "modify library"],
            "library_delete": ["delete library", "remove library"],
            "user_access": ["user access", "permissions", "who can access", "user permissions", "check user", "access management"],
            "help": ["help", "what can you do", "commands", "assistance", "what can you help", "need help"],
            "status": ["status", "current state", "system status", "what's the status"]
        }
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process a user request and generate an appropriate response"""
        try:
            logger.info(f"Processing agent request from session {request.session_id}")
            
            # Detect user intent
            intent = self._detect_intent(request.user_message)
            
            # Update conversation
            await self.conversation_service.add_message(
                request.session_id,
                ConversationMessage(
                    id=str(uuid.uuid4()),
                    role=MessageRole.USER,
                    content=request.user_message
                )
            )
            
            # Process based on intent
            response = await self._process_intent(intent, request)
            
            # Add agent response to conversation
            await self.conversation_service.add_message(
                request.session_id,
                ConversationMessage(
                    id=str(uuid.uuid4()),
                    role=MessageRole.ASSISTANT,
                    content=response.content
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing agent request: {e}")
            return AgentResponse(
                response_type=AgentResponseType.ERROR,
                content=f"I encountered an error while processing your request: {str(e)}",
                suggestions=["Please try rephrasing your request", "Ask for help if you need assistance"]
            )
    
    def _detect_intent(self, message: str) -> AgentIntent:
        """Simple intent detection based on keyword matching"""
        message_lower = message.lower()
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return AgentIntent(
                        intent_type=intent_type,
                        confidence=0.8,
                        entities={},
                        parameters={}
                    )
        
        # Default to general query
        return AgentIntent(
            intent_type="general_query",
            confidence=0.5,
            entities={},
            parameters={}
        )
    
    async def _process_intent(self, intent: AgentIntent, request: AgentRequest) -> AgentResponse:
        """Process the detected intent and generate appropriate response"""
        
        if intent.intent_type == "library_list":
            return await self._handle_library_list(request)
        elif intent.intent_type == "library_create":
            return await self._handle_library_create(request)
        elif intent.intent_type == "user_access":
            return await self._handle_user_access(request)
        elif intent.intent_type == "help":
            return await self._handle_help(request)
        elif intent.intent_type == "status":
            return await self._handle_status(request)
        else:
            return await self._handle_general_query(request)
    
    async def _handle_library_list(self, request: AgentRequest) -> AgentResponse:
        """Handle request to list external libraries"""
        try:
            libraries = await self.integration_service.get_active_libraries()
            
            if not libraries:
                content = "No external libraries are currently configured."
                suggestions = ["Would you like me to help you create a new library?"]
            else:
                library_list = "\n".join([f"• {lib.name} - {lib.url}" for lib in libraries])
                content = f"Here are the currently configured external libraries:\n\n{library_list}"
                suggestions = [
                    "Would you like details about a specific library?",
                    "Do you need to modify any of these libraries?"
                ]
            
            return AgentResponse(
                response_type=AgentResponseType.TEXT,
                content=content,
                suggestions=suggestions,
                metadata={"library_count": len(libraries)}
            )
            
        except Exception as e:
            return AgentResponse(
                response_type=AgentResponseType.ERROR,
                content=f"I couldn't retrieve the library list: {str(e)}"
            )
    
    async def _handle_library_create(self, request: AgentRequest) -> AgentResponse:
        """Handle request to create a new library"""
        content = """I can help you create a new external library. To get started, I'll need the following information:

1. **Library Name** - A descriptive name for the library
2. **SharePoint URL** - The complete URL to the SharePoint library
3. **Description** - Optional description of the library's purpose
4. **External Users** - Email addresses of users who should have access

Would you like to proceed with creating a new library? Please provide the library name and URL to begin."""
        
        actions = [
            AgentAction(
                action_type="library_creation_wizard",
                parameters={},
                description="Start the library creation process",
                requires_confirmation=True
            )
        ]
        
        return AgentResponse(
            response_type=AgentResponseType.ACTION,
            content=content,
            actions=actions,
            suggestions=[
                "Provide the library name and URL",
                "Cancel library creation"
            ]
        )
    
    async def _handle_user_access(self, request: AgentRequest) -> AgentResponse:
        """Handle request about user access and permissions"""
        try:
            stats = await self.integration_service.get_library_statistics()
            
            content = f"""Here's a summary of user access across your external libraries:

📊 **Access Statistics:**
• Total Libraries: {stats.total_libraries}
• Active Libraries: {stats.active_libraries}
• Total External Users: {stats.total_external_users}

To get specific access information, please let me know:
- Which library you'd like to check
- Which user's access you want to review
- If you need to modify permissions for someone"""
            
            return AgentResponse(
                response_type=AgentResponseType.TEXT,
                content=content,
                suggestions=[
                    "Check access for a specific library",
                    "Review user permissions",
                    "Add or remove user access"
                ]
            )
            
        except Exception as e:
            return AgentResponse(
                response_type=AgentResponseType.ERROR,
                content=f"I couldn't retrieve access information: {str(e)}"
            )
    
    async def _handle_help(self, request: AgentRequest) -> AgentResponse:
        """Provide help information"""
        content = """🤖 **External Collaboration Management Copilot**

I'm here to help you manage external SharePoint libraries and user access. Here's what I can do:

**📚 Library Management:**
• List all external libraries
• Create new libraries
• Update existing libraries
• Delete or archive libraries
• Test library connections

**👥 User Access Control:**
• View user permissions
• Add external users to libraries
• Remove user access
• Review access statistics

**💬 How to interact with me:**
• Use natural language - just tell me what you need
• Ask questions like "Show me all libraries" or "Help me create a new library"
• I'll guide you through any complex tasks step by step

**🔍 Quick Commands:**
• "List libraries" - Show all external libraries
• "User access" - Review permissions and access
• "Create library" - Start creating a new library
• "System status" - Check system health

What would you like to do today?"""
        
        return AgentResponse(
            response_type=AgentResponseType.HELP,
            content=content,
            suggestions=[
                "List all libraries",
                "Check user access",
                "Create a new library",
                "System status"
            ]
        )
    
    async def _handle_status(self, request: AgentRequest) -> AgentResponse:
        """Handle system status request"""
        try:
            stats = await self.integration_service.get_library_statistics()
            
            content = f"""🔧 **System Status Report**

**📊 External Libraries:**
• Total: {stats.total_libraries}
• Active: {stats.active_libraries}
• Deleted: {stats.deleted_libraries}

**👥 User Access:**
• Total External Users: {stats.total_external_users}

**🔄 Recent Activity:**
"""
            
            # Add recent activity
            for activity in stats.recent_activity[:3]:  # Show last 3 activities
                content += f"• {activity['action'].title()} library '{activity['library_name']}' by {activity['admin_user']}\n"
            
            content += "\n✅ All systems operational"
            
            return AgentResponse(
                response_type=AgentResponseType.TEXT,
                content=content,
                suggestions=[
                    "View detailed library information",
                    "Check specific library status",
                    "Review system logs"
                ]
            )
            
        except Exception as e:
            return AgentResponse(
                response_type=AgentResponseType.ERROR,
                content=f"I couldn't retrieve system status: {str(e)}"
            )
    
    async def _handle_general_query(self, request: AgentRequest) -> AgentResponse:
        """Handle general queries that don't match specific intents"""
        content = """I understand you have a question about external collaboration management. 

I can help you with:
• Managing external SharePoint libraries
• Controlling user access and permissions  
• Creating and updating library configurations
• Reviewing system status and statistics

Could you please be more specific about what you'd like to do? For example:
• "Show me all libraries"
• "Help me add a new library"
• "Check user permissions"
• "What's the system status?"
"""
        
        return AgentResponse(
            response_type=AgentResponseType.TEXT,
            content=content,
            suggestions=[
                "List all libraries",
                "Create new library", 
                "Check user access",
                "Get help"
            ]
        )