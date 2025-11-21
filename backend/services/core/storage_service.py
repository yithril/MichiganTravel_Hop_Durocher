"""Storage service that orchestrates storage operations and database metadata."""
from typing import BinaryIO, Optional
from core.models.image import Image
from services.core.storage_interface import StorageInterface
from services.core.storage_exceptions import StorageError, ImageNotFoundError
from dtos.storage_dto import ImageMetadataResponse, ImageUploadResponse, ImageListResponse


class StorageService:
    """Service for handling image storage operations with database metadata."""
    
    def __init__(self, storage_backend: StorageInterface):
        """
        Initialize storage service with a storage backend.
        
        Args:
            storage_backend: Implementation of StorageInterface (e.g., S3Storage)
        """
        self.storage = storage_backend
    
    async def upload_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        filename: str,
        file_content: BinaryIO,
        content_type: str,
    ) -> ImageUploadResponse:
        """
        Upload an image and save metadata to database.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            filename: Original filename
            file_content: File content as binary stream
            content_type: MIME type of the file
            
        Returns:
            ImageUploadResponse with metadata and URL
            
        Raises:
            StorageError: If upload or database operation fails
        """
        # Get file size
        file_content.seek(0, 2)  # Seek to end
        file_size = file_content.tell()
        file_content.seek(0)  # Reset to beginning
        
        # Save to storage
        s3_key = await self.storage.save_image(
            user_id=user_id,
            trip_id=trip_id,
            trip_day_id=trip_day_id,
            filename=filename,
            file_content=file_content,
            content_type=content_type,
        )
        
        # Generate presigned URL
        url = await self.storage.get_presigned_url(s3_key)
        
        # Save metadata to database
        try:
            image = await Image.create(
                user_id=user_id,
                trip_id=trip_id,
                trip_day_id=trip_day_id,
                filename=filename,
                s3_key=s3_key,
                url=url,
                file_size=file_size,
                content_type=content_type,
            )
            
            return ImageUploadResponse(
                id=image.id,
                user_id=image.user_id,
                trip_id=image.trip_id,
                trip_day_id=image.trip_day_id,
                filename=image.filename,
                s3_key=image.s3_key,
                url=image.url,
                file_size=image.file_size,
                content_type=image.content_type,
                created_at=image.created_at.isoformat(),
            )
            
        except Exception as e:
            # If database save fails, try to clean up the uploaded file
            try:
                await self.storage.delete_image(user_id, trip_id, trip_day_id, s3_key)
            except Exception:
                pass  # Ignore cleanup errors
            
            raise StorageError(f"Failed to save image metadata to database: {str(e)}") from e
    
    async def get_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        image_id: int,
    ) -> tuple[bytes, str]:
        """
        Retrieve an image file and its content type.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            image_id: Image ID from database
            
        Returns:
            Tuple of (image_bytes, content_type)
            
        Raises:
            ImageNotFoundError: If image doesn't exist
            StorageError: If retrieval fails
        """
        # Get metadata from database
        image = await Image.get_or_none(
            id=image_id,
            user_id=user_id,
            trip_id=trip_id,
            trip_day_id=trip_day_id,
        )
        
        if not image:
            raise ImageNotFoundError(
                f"Image {image_id} not found for user {user_id}, "
                f"trip {trip_id}, trip_day {trip_day_id}"
            )
        
        # Get file from storage
        image_bytes = await self.storage.get_image(
            user_id=user_id,
            trip_id=trip_id,
            trip_day_id=trip_day_id,
            s3_key=image.s3_key,
        )
        
        return image_bytes, image.content_type
    
    async def get_image_metadata(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        image_id: int,
    ) -> ImageMetadataResponse:
        """
        Get image metadata from database.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            image_id: Image ID
            
        Returns:
            ImageMetadataResponse with metadata
            
        Raises:
            ImageNotFoundError: If image doesn't exist
        """
        image = await Image.get_or_none(
            id=image_id,
            user_id=user_id,
            trip_id=trip_id,
            trip_day_id=trip_day_id,
        )
        
        if not image:
            raise ImageNotFoundError(
                f"Image {image_id} not found for user {user_id}, "
                f"trip {trip_id}, trip_day {trip_day_id}"
            )
        
        # Regenerate URL if needed (presigned URLs expire)
        url = await self.storage.get_presigned_url(image.s3_key)
        
        # Update URL in database if it changed
        if image.url != url:
            image.url = url
            await image.save()
        
        return ImageMetadataResponse(
            id=image.id,
            user_id=image.user_id,
            trip_id=image.trip_id,
            trip_day_id=image.trip_day_id,
            filename=image.filename,
            s3_key=image.s3_key,
            url=image.url,
            file_size=image.file_size,
            content_type=image.content_type,
            created_at=image.created_at.isoformat(),
            updated_at=image.updated_at.isoformat(),
        )
    
    async def list_images(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
    ) -> ImageListResponse:
        """
        List all images for a specific trip day.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            
        Returns:
            ImageListResponse with list of images
        """
        images = await Image.filter(
            user_id=user_id,
            trip_id=trip_id,
            trip_day_id=trip_day_id,
        ).order_by('-created_at')
        
        # Regenerate URLs for all images
        image_responses = []
        for image in images:
            url = await self.storage.get_presigned_url(image.s3_key)
            
            # Update URL in database if it changed
            if image.url != url:
                image.url = url
                await image.save()
            
            image_responses.append(
                ImageMetadataResponse(
                    id=image.id,
                    user_id=image.user_id,
                    trip_id=image.trip_id,
                    trip_day_id=image.trip_day_id,
                    filename=image.filename,
                    s3_key=image.s3_key,
                    url=image.url,
                    file_size=image.file_size,
                    content_type=image.content_type,
                    created_at=image.created_at.isoformat(),
                    updated_at=image.updated_at.isoformat(),
                )
            )
        
        return ImageListResponse(
            images=image_responses,
            total=len(image_responses),
        )
    
    async def delete_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        image_id: int,
    ) -> None:
        """
        Delete an image from storage and database.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            image_id: Image ID
            
        Raises:
            ImageNotFoundError: If image doesn't exist
            StorageError: If deletion fails
        """
        # Get metadata from database
        image = await Image.get_or_none(
            id=image_id,
            user_id=user_id,
            trip_id=trip_id,
            trip_day_id=trip_day_id,
        )
        
        if not image:
            raise ImageNotFoundError(
                f"Image {image_id} not found for user {user_id}, "
                f"trip {trip_id}, trip_day {trip_day_id}"
            )
        
        s3_key = image.s3_key
        
        # Delete from storage first
        await self.storage.delete_image(
            user_id=user_id,
            trip_id=trip_id,
            trip_day_id=trip_day_id,
            s3_key=s3_key,
        )
        
        # Delete from database
        await image.delete()

