"""Service for managing conversation history."""
from typing import Optional, List
from core.models.conversation import Conversation, Message
from dtos.agent_dto import ConversationResponse, MessageResponse


class ConversationService:
    """Service for managing agent conversation history."""
    
    async def create_conversation(
        self,
        user_id: int,
        trip_id: Optional[int] = None,
        agent_name: Optional[str] = None,
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            user_id: User ID
            trip_id: Optional trip ID
            agent_name: Optional agent name identifier
            
        Returns:
            Created Conversation object
        """
        conversation = await Conversation.create(
            user_id=user_id,
            trip_id=trip_id,
            agent_name=agent_name,
        )
        return conversation
    
    async def get_conversation(
        self,
        conversation_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            user_id: Optional user ID for validation
            
        Returns:
            Conversation object or None if not found
        """
        if user_id:
            return await Conversation.get_or_none(
                id=conversation_id,
                user_id=user_id,
            )
        return await Conversation.get_or_none(id=conversation_id)
    
    async def get_user_conversations(
        self,
        user_id: int,
        trip_id: Optional[int] = None,
        limit: int = 50,
    ) -> List[Conversation]:
        """
        Get conversations for a user, optionally filtered by trip.
        
        Args:
            user_id: User ID
            trip_id: Optional trip ID filter
            limit: Maximum number of conversations to return
            
        Returns:
            List of Conversation objects, ordered by most recent
        """
        query = Conversation.filter(user_id=user_id)
        
        if trip_id:
            query = query.filter(trip_id=trip_id)
        
        return await query.order_by('-created_at').limit(limit)
    
    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> Message:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role ("user", "assistant", "system")
            content: Message content
            
        Returns:
            Created Message object
            
        Raises:
            ValueError: If conversation doesn't exist
        """
        conversation = await Conversation.get_or_none(id=conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = await Message.create(
            conversation=conversation,
            role=role,
            content=content,
        )
        
        # Update conversation timestamp
        await conversation.save()
        
        return message
    
    async def get_conversation_messages(
        self,
        conversation_id: int,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """
        Get all messages for a conversation, ordered chronologically.
        
        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages
            
        Returns:
            List of Message objects, ordered by creation time
        """
        query = Message.filter(conversation_id=conversation_id).order_by('created_at')
        
        if limit:
            return await query.limit(limit)
        
        return await query
    
    async def delete_conversation(
        self,
        conversation_id: int,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: Conversation ID
            user_id: Optional user ID for validation
            
        Returns:
            True if deleted, False if not found
        """
        conversation = await Conversation.get_or_none(id=conversation_id)
        
        if not conversation:
            return False
        
        if user_id and conversation.user_id != user_id:
            raise ValueError("Conversation does not belong to user")
        
        await conversation.delete()
        return True
    
    async def get_conversation_response(
        self,
        conversation_id: int,
    ) -> ConversationResponse:
        """
        Get a conversation with its messages as a response DTO.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            ConversationResponse with messages
            
        Raises:
            ValueError: If conversation doesn't exist
        """
        conversation = await Conversation.get_or_none(id=conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        messages = await self.get_conversation_messages(conversation_id)
        
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            trip_id=conversation.trip_id,
            agent_name=conversation.agent_name,
            messages=[
                MessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                )
                for msg in messages
            ],
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
        )

