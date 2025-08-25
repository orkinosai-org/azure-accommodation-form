"""
Conversation Service for Copilot Agent

Manages conversation sessions and message history.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, List

from app.copilot.models.conversation import (
    ConversationSession, ConversationMessage, ConversationCreate, MessageCreate
)

logger = logging.getLogger(__name__)

# In-memory storage for conversations (use database in production)
conversations = {}


class ConversationService:
    """Service for managing conversation sessions"""
    
    def __init__(self):
        pass
    
    async def create_conversation(self, conversation_data: ConversationCreate) -> ConversationSession:
        """Create a new conversation session"""
        conversation_id = str(uuid.uuid4())
        
        # Create initial conversation
        conversation = ConversationSession(
            id=conversation_id,
            user_id=conversation_data.user_id,
            title=conversation_data.title or "New Conversation",
            context=conversation_data.context or {}
        )
        
        # Add initial message if provided
        if conversation_data.initial_message:
            initial_msg = ConversationMessage(
                id=str(uuid.uuid4()),
                role="user",
                content=conversation_data.initial_message
            )
            conversation.messages.append(initial_msg)
        
        conversations[conversation_id] = conversation.dict()
        logger.info(f"Created new conversation: {conversation_id}")
        
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationSession]:
        """Get a conversation by ID"""
        conversation_data = conversations.get(conversation_id)
        if conversation_data:
            return ConversationSession(**conversation_data)
        return None
    
    async def get_or_create_conversation(self, session_id: str, user_id: Optional[str] = None) -> ConversationSession:
        """Get existing conversation or create a new one"""
        conversation = await self.get_conversation(session_id)
        
        if not conversation:
            # Create new conversation
            conversation_data = ConversationCreate(
                user_id=user_id,
                title="Copilot Assistance"
            )
            conversation = await self.create_conversation(conversation_data)
            # Update the conversations dict with the correct session_id
            conversations[session_id] = conversation.dict()
            conversation.id = session_id
        
        return conversation
    
    async def add_message(self, conversation_id: str, message: ConversationMessage) -> bool:
        """Add a message to a conversation"""
        conversation_data = conversations.get(conversation_id)
        
        if not conversation_data:
            # Create conversation if it doesn't exist
            await self.get_or_create_conversation(conversation_id)
            conversation_data = conversations[conversation_id]
        
        conversation = ConversationSession(**conversation_data)
        conversation.messages.append(message)
        conversation.updated_at = datetime.utcnow()
        
        conversations[conversation_id] = conversation.dict()
        logger.info(f"Added message to conversation {conversation_id}")
        
        return True
    
    async def update_conversation_context(self, conversation_id: str, context: Dict) -> bool:
        """Update conversation context"""
        conversation_data = conversations.get(conversation_id)
        if not conversation_data:
            return False
        
        conversation = ConversationSession(**conversation_data)
        conversation.context = {**(conversation.context or {}), **context}
        conversation.updated_at = datetime.utcnow()
        
        conversations[conversation_id] = conversation.dict()
        logger.info(f"Updated context for conversation {conversation_id}")
        
        return True
    
    async def list_user_conversations(self, user_id: str, limit: int = 50) -> List[ConversationSession]:
        """List conversations for a user"""
        user_conversations = []
        
        for conv_data in conversations.values():
            conversation = ConversationSession(**conv_data)
            if conversation.user_id == user_id and conversation.is_active:
                user_conversations.append(conversation)
        
        # Sort by last update time (newest first)
        user_conversations.sort(key=lambda x: x.updated_at, reverse=True)
        
        return user_conversations[:limit]
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Mark conversation as inactive (soft delete)"""
        conversation_data = conversations.get(conversation_id)
        if not conversation_data:
            return False
        
        conversation = ConversationSession(**conversation_data)
        conversation.is_active = False
        conversation.updated_at = datetime.utcnow()
        
        conversations[conversation_id] = conversation.dict()
        logger.info(f"Deleted conversation {conversation_id}")
        
        return True
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[ConversationMessage]:
        """Get messages from a conversation"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        # Return most recent messages
        return conversation.messages[-limit:] if conversation.messages else []