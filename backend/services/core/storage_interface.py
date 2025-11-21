"""Abstract interface for storage operations."""
from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageInterface(ABC):
    """Abstract interface for storage backends (S3, local filesystem, etc.)."""
    
    @abstractmethod
    async def save_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        filename: str,
        file_content: BinaryIO,
        content_type: str,
    ) -> str:
        """
        Save an image to storage.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            filename: Original filename
            file_content: File content as binary stream
            content_type: MIME type of the file
            
        Returns:
            S3 key/path where the file was saved
            
        Raises:
            StorageError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        s3_key: str,
    ) -> bytes:
        """
        Retrieve an image from storage.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            s3_key: S3 key/path of the file
            
        Returns:
            Image file content as bytes
            
        Raises:
            ImageNotFoundError: If image doesn't exist
            StorageError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def delete_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        s3_key: str,
    ) -> None:
        """
        Delete an image from storage.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            s3_key: S3 key/path of the file to delete
            
        Raises:
            ImageNotFoundError: If image doesn't exist
            StorageError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def get_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
    ) -> str:
        """
        Generate a presigned URL for accessing an image.
        
        Args:
            s3_key: S3 key/path of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL string
            
        Raises:
            StorageError: If URL generation fails
        """
        pass

