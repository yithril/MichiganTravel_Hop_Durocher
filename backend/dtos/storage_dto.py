"""Data Transfer Objects for storage operations."""
from pydantic import BaseModel


class ImageMetadataResponse(BaseModel):
    """Response DTO for image metadata."""
    id: int
    user_id: int
    trip_id: int
    trip_day_id: int
    filename: str
    s3_key: str
    url: str
    file_size: int
    content_type: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    """Response DTO after image upload."""
    id: int
    user_id: int
    trip_id: int
    trip_day_id: int
    filename: str
    s3_key: str
    url: str
    file_size: int
    content_type: str
    created_at: str
    
    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    """Response DTO for listing images."""
    images: list[ImageMetadataResponse]
    total: int

