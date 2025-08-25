"""
Task Service for Copilot Agent

Manages task execution and automation.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, List

from app.copilot.models.task import (
    Task, TaskCreate, TaskUpdate, TaskStatus, TaskType
)

logger = logging.getLogger(__name__)

# In-memory storage for tasks (use database in production)
tasks = {}


class TaskService:
    """Service for managing and executing tasks"""
    
    def __init__(self):
        pass
    
    async def create_task(self, task_data: TaskCreate, admin_user: str = "system") -> Task:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            conversation_id=task_data.conversation_id,
            user_id=task_data.user_id,
            title=task_data.title,
            description=task_data.description,
            task_type=task_data.task_type,
            priority=task_data.priority,
            parameters=task_data.parameters or {}
        )
        
        tasks[task_id] = task.dict()
        logger.info(f"Created task: {task_id} - {task.title}")
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        task_data = tasks.get(task_id)
        if task_data:
            return Task(**task_data)
        return None
    
    async def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task"""
        task_data = tasks.get(task_id)
        if not task_data:
            return None
        
        task = Task(**task_data)
        
        # Update only provided fields
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(task, field):
                setattr(task, field, value)
        
        # Update timestamps based on status changes
        if task_update.status:
            if task_update.status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.utcnow()
            elif task_update.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = datetime.utcnow()
        
        task.updated_at = datetime.utcnow()
        
        tasks[task_id] = task.dict()
        logger.info(f"Updated task: {task_id} - Status: {task.status}")
        
        return task
    
    async def execute_task(self, task_id: str) -> bool:
        """Execute a task based on its type"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        try:
            # Update task status to in progress
            await self.update_task(task_id, TaskUpdate(
                status=TaskStatus.IN_PROGRESS,
                execution_steps=["Task execution started"]
            ))
            
            # Execute based on task type
            success = False
            if task.task_type == TaskType.LIBRARY_MANAGEMENT:
                success = await self._execute_library_management_task(task)
            elif task.task_type == TaskType.USER_ACCESS:
                success = await self._execute_user_access_task(task)
            elif task.task_type == TaskType.EXTERNAL_COLLABORATION:
                success = await self._execute_external_collaboration_task(task)
            elif task.task_type == TaskType.INFORMATION_RETRIEVAL:
                success = await self._execute_information_retrieval_task(task)
            elif task.task_type == TaskType.REPORTING:
                success = await self._execute_reporting_task(task)
            else:
                logger.warning(f"Unknown task type: {task.task_type}")
                success = False
            
            # Update final task status
            final_status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            await self.update_task(task_id, TaskUpdate(
                status=final_status,
                progress=100.0 if success else 0.0
            ))
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            await self.update_task(task_id, TaskUpdate(
                status=TaskStatus.FAILED,
                error_message=str(e)
            ))
            return False
    
    async def _execute_library_management_task(self, task: Task) -> bool:
        """Execute library management task"""
        # This would integrate with the external library service
        logger.info(f"Executing library management task: {task.title}")
        
        # Add execution steps
        steps = task.execution_steps or []
        steps.append("Library management task completed")
        
        await self.update_task(task.id, TaskUpdate(
            execution_steps=steps,
            progress=100.0,
            result={"status": "completed", "message": "Library management task executed successfully"}
        ))
        
        return True
    
    async def _execute_user_access_task(self, task: Task) -> bool:
        """Execute user access task"""
        logger.info(f"Executing user access task: {task.title}")
        
        steps = task.execution_steps or []
        steps.append("User access task completed")
        
        await self.update_task(task.id, TaskUpdate(
            execution_steps=steps,
            progress=100.0,
            result={"status": "completed", "message": "User access task executed successfully"}
        ))
        
        return True
    
    async def _execute_external_collaboration_task(self, task: Task) -> bool:
        """Execute external collaboration task"""
        logger.info(f"Executing external collaboration task: {task.title}")
        
        steps = task.execution_steps or []
        steps.append("External collaboration task completed")
        
        await self.update_task(task.id, TaskUpdate(
            execution_steps=steps,
            progress=100.0,
            result={"status": "completed", "message": "External collaboration task executed successfully"}
        ))
        
        return True
    
    async def _execute_information_retrieval_task(self, task: Task) -> bool:
        """Execute information retrieval task"""
        logger.info(f"Executing information retrieval task: {task.title}")
        
        steps = task.execution_steps or []
        steps.append("Information retrieval task completed")
        
        await self.update_task(task.id, TaskUpdate(
            execution_steps=steps,
            progress=100.0,
            result={"status": "completed", "message": "Information retrieval task executed successfully"}
        ))
        
        return True
    
    async def _execute_reporting_task(self, task: Task) -> bool:
        """Execute reporting task"""
        logger.info(f"Executing reporting task: {task.title}")
        
        steps = task.execution_steps or []
        steps.append("Reporting task completed")
        
        await self.update_task(task.id, TaskUpdate(
            execution_steps=steps,
            progress=100.0,
            result={"status": "completed", "message": "Reporting task executed successfully"}
        ))
        
        return True
    
    async def list_tasks(
        self, 
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 50
    ) -> List[Task]:
        """List tasks with optional filtering"""
        task_list = []
        
        for task_data in tasks.values():
            task = Task(**task_data)
            
            # Apply filters
            if conversation_id and task.conversation_id != conversation_id:
                continue
            if user_id and task.user_id != user_id:
                continue
            if status and task.status != status:
                continue
            
            task_list.append(task)
        
        # Sort by creation time (newest first)
        task_list.sort(key=lambda x: x.created_at, reverse=True)
        
        return task_list[:limit]
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in tasks:
            del tasks[task_id]
            logger.info(f"Deleted task: {task_id}")
            return True
        return False