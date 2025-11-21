"""Conversation and Message models for agent chat history."""
from tortoise import fields
from core.models.base import BaseModel


class Conversation(BaseModel):
    """Conversation model for tracking agent chat sessions."""
    
    user_id = fields.IntField(index=True)
    trip_id = fields.IntField(null=True, index=True)  # Optional trip context
    agent_name = fields.CharField(max_length=100, null=True)  # Optional: which agent was used
    
    class Meta:
        table = "conversations"
        indexes = [
            ("user_id", "trip_id"),  # Composite index for queries
        ]
    
    def __str__(self):
        return f"Conversation(id={self.id}, user_id={self.user_id}, trip_id={self.trip_id})"


class Message(BaseModel):
    """Message model for storing individual messages in conversations."""
    
    conversation = fields.ForeignKeyField(
        "models.Conversation",
        related_name="messages",
        on_delete=fields.CASCADE
    )
    role = fields.CharField(max_length=20)  # "user", "assistant", "system"
    content = fields.TextField()
    sequence_index = fields.IntField()  # For explicit ordering of messages
    
    class Meta:
        table = "messages"
        indexes = [
            ("conversation_id", "created_at"),  # For ordered message retrieval
            ("conversation_id", "sequence_index"),  # For sequence-based ordering
        ]
    
    def __str__(self):
        return f"Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id}, sequence_index={self.sequence_index})"

