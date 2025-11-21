"""Vibe model for city and attraction categorization."""
from tortoise import fields
from core.models.base import BaseModel


class Vibe(BaseModel):
    """Vibe model for high-level categorization."""
    
    code = fields.CharField(max_length=100, unique=True)  # e.g., "lakeside_peaceful"
    label = fields.CharField(max_length=255)  # e.g., "Lakeside & peaceful"
    description = fields.TextField(null=True)
    
    class Meta:
        table = "vibes"
    
    def __str__(self):
        return f"Vibe(code={self.code}, label={self.label})"

