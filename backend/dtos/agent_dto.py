"""Data Transfer Objects for agent conversation operations."""
from typing import Optional, List
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Response DTO for a message."""
    id: int
    role: str
    content: str
    created_at: str
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response DTO for a conversation with messages."""
    id: int
    user_id: int
    trip_id: Optional[int]
    agent_name: Optional[str]
    messages: List[MessageResponse]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Response DTO for listing conversations."""
    conversations: List[ConversationResponse]
    total: int
