"""Image model for storing image metadata."""
from tortoise import fields
from core.models.base import BaseModel


class Image(BaseModel):
    """Image model with metadata for user trip photos."""
    
    user_id = fields.IntField(index=True)
    trip_id = fields.IntField(index=True)
    trip_day_id = fields.IntField(index=True)
    filename = fields.CharField(max_length=255)
    s3_key = fields.CharField(max_length=512, unique=True, index=True)
    url = fields.CharField(max_length=1024)  # Presigned URL
    file_size = fields.IntField()  # Size in bytes
    content_type = fields.CharField(max_length=100)  # MIME type
    
    class Meta:
        table = "images"
        indexes = [
            ("user_id", "trip_id", "trip_day_id"),  # Composite index for queries
        ]
    
    def __str__(self):
        return f"Image(id={self.id}, user_id={self.user_id}, trip_id={self.trip_id}, s3_key={self.s3_key})"

