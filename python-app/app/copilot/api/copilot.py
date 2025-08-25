"""
Copilot Agent API Routes

FastAPI routes for the External Collaboration Management Copilot Agent.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from fastapi.responses import JSONResponse

from app.copilot.models.agent import AgentRequest, AgentResponse
from app.copilot.models.conversation import ConversationSession, ConversationCreate
from app.copilot.models.task import Task, TaskCreate, TaskUpdate
from app.copilot.services.agent_service import CopilotAgentService
from app.copilot.services.conversation_service import ConversationService
from app.copilot.services.task_service import TaskService

router = APIRouter()
logger = logging.getLogger(__name__)

# Service instances
agent_service = CopilotAgentService()
conversation_service = ConversationService()
task_service = TaskService()


@router.post("/chat", response_model=AgentResponse)
async def chat_with_copilot(request: AgentRequest):
    """
    Chat with the Copilot agent
    
    Send a message to the Copilot agent and receive an intelligent response
    with suggestions and possible actions.
    """
    try:
        logger.info(f"Chat request from session {request.session_id}")
        response = await agent_service.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/conversations", response_model=ConversationSession, status_code=status.HTTP_201_CREATED)
async def create_conversation(conversation_data: ConversationCreate):
    """Create a new conversation session"""
    try:
        conversation = await conversation_service.create_conversation(conversation_data)
        logger.info(f"Created conversation {conversation.id}")
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationSession)
async def get_conversation(conversation_id: str):
    """Get a specific conversation by ID"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationSession])
async def list_conversations(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of conversations to return")
):
    """List conversations, optionally filtered by user"""
    try:
        if user_id:
            conversations = await conversation_service.list_user_conversations(user_id, limit)
        else:
            # For demo purposes, return empty list if no user_id specified
            # In production, you might want to require authentication
            conversations = []
        
        logger.info(f"Retrieved {len(conversations)} conversations")
        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing conversations: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete (deactivate) a conversation"""
    try:
        success = await conversation_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )


@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    """Create a new task"""
    try:
        task = await task_service.create_task(task_data)
        logger.info(f"Created task {task.id}")
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get a specific task by ID"""
    try:
        task = await task_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    try:
        task = await task_service.update_task(task_id, task_update)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        logger.info(f"Updated task {task_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}"
        )


@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    """Execute a task"""
    try:
        success = await task_service.execute_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task execution failed"
            )
        return {"message": "Task executed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing task: {str(e)}"
        )


@router.get("/tasks", response_model=List[Task])
async def list_tasks(
    conversation_id: Optional[str] = Query(None, description="Filter by conversation ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return")
):
    """List tasks with optional filtering"""
    try:
        tasks = await task_service.list_tasks(
            conversation_id=conversation_id,
            user_id=user_id,
            status=status,
            limit=limit
        )
        logger.info(f"Retrieved {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tasks: {str(e)}"
        )


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    try:
        success = await task_service.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}"
        )


@router.get("/capabilities")
async def get_agent_capabilities():
    """Get available Copilot agent capabilities"""
    capabilities = [
        {
            "name": "External Library Management",
            "description": "Manage external SharePoint libraries, create, update, and delete libraries",
            "actions": ["list_libraries", "create_library", "update_library", "delete_library"]
        },
        {
            "name": "User Access Control", 
            "description": "Control user access and permissions for external libraries",
            "actions": ["check_access", "grant_access", "revoke_access", "list_users"]
        },
        {
            "name": "Conversation Management",
            "description": "Manage conversation sessions and message history",
            "actions": ["create_conversation", "list_conversations", "delete_conversation"]
        },
        {
            "name": "Task Automation",
            "description": "Create and execute automated tasks for collaboration management",
            "actions": ["create_task", "execute_task", "monitor_task", "list_tasks"]
        },
        {
            "name": "Help & Documentation",
            "description": "Provide help and guidance for using the system",
            "actions": ["get_help", "show_commands", "explain_features"]
        }
    ]
    
    return {
        "capabilities": capabilities,
        "version": "1.0.0",
        "status": "active"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for the Copilot agent"""
    try:
        # Basic health checks
        stats = await agent_service.integration_service.get_library_statistics()
        
        return {
            "status": "healthy",
            "service": "External Collaboration Management Copilot",
            "version": "1.0.0",
            "components": {
                "agent_service": "operational",
                "conversation_service": "operational", 
                "task_service": "operational",
                "integration_service": "operational"
            },
            "external_libraries": {
                "total": stats.total_libraries,
                "active": stats.active_libraries
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )