"""S3-compatible storage implementation for IBM Cloud Object Storage."""
import uuid
from typing import BinaryIO
import aioboto3
from botocore.exceptions import ClientError, BotoCoreError
from core.config import settings
from services.core.storage_interface import StorageInterface
from services.core.storage_exceptions import StorageError, ImageNotFoundError, StorageConfigurationError


class S3Storage(StorageInterface):
    """S3-compatible storage implementation using aioboto3."""
    
    def __init__(self):
        """Initialize S3 storage client."""
        if not all([
            settings.s3_endpoint,
            settings.s3_access_key,
            settings.s3_secret_key,
            settings.s3_bucket_name,
        ]):
            raise StorageConfigurationError(
                "S3 configuration is incomplete. Required: S3_ENDPOINT, "
                "S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_NAME"
            )
        
        self.endpoint_url = settings.s3_endpoint
        self.access_key = settings.s3_access_key
        self.secret_key = settings.s3_secret_key
        self.bucket_name = settings.s3_bucket_name
        self.use_ssl = settings.s3_use_ssl
        self.region = settings.s3_region
        
        # Create session for async operations
        self.session = aioboto3.Session()
    
    def _build_s3_key(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        filename: str,
    ) -> str:
        """
        Build S3 key from user/trip/tripday structure.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            filename: Original filename
            
        Returns:
            S3 key path: {user_id}/{trip_id}/{trip_day_id}/{unique_filename}
        """
        # Generate unique filename to avoid collisions
        file_ext = filename.split('.')[-1] if '.' in filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}" if file_ext else uuid.uuid4().hex
        
        return f"{user_id}/{trip_id}/{trip_day_id}/{unique_filename}"
    
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
        Save an image to S3 storage.
        
        Args:
            user_id: User ID
            trip_id: Trip ID
            trip_day_id: Trip day ID
            filename: Original filename
            file_content: File content as binary stream
            content_type: MIME type of the file
            
        Returns:
            S3 key where the file was saved
            
        Raises:
            StorageError: If save operation fails
        """
        s3_key = self._build_s3_key(user_id, trip_id, trip_day_id, filename)
        
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
                region_name=self.region,
            ) as s3:
                # Read file content
                file_content.seek(0)
                file_bytes = await file_content.read()
                
                # Upload to S3
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_bytes,
                    ContentType=content_type,
                )
                
                return s3_key
                
        except (ClientError, BotoCoreError) as e:
            raise StorageError(f"Failed to save image to S3: {str(e)}") from e
        except Exception as e:
            raise StorageError(f"Unexpected error saving image: {str(e)}") from e
    
    async def get_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        s3_key: str,
    ) -> bytes:
        """
        Retrieve an image from S3 storage.
        
        Args:
            user_id: User ID (for validation)
            trip_id: Trip ID (for validation)
            trip_day_id: Trip day ID (for validation)
            s3_key: S3 key/path of the file
            
        Returns:
            Image file content as bytes
            
        Raises:
            ImageNotFoundError: If image doesn't exist
            StorageError: If retrieval fails
        """
        # Validate that s3_key matches the expected structure
        expected_prefix = f"{user_id}/{trip_id}/{trip_day_id}/"
        if not s3_key.startswith(expected_prefix):
            raise StorageError(
                f"S3 key {s3_key} does not match expected structure "
                f"for user {user_id}, trip {trip_id}, trip_day {trip_day_id}"
            )
        
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
                region_name=self.region,
            ) as s3:
                response = await s3.get_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                )
                
                # Read the entire file content
                file_content = await response['Body'].read()
                return file_content
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchKey':
                raise ImageNotFoundError(f"Image not found: {s3_key}") from e
            raise StorageError(f"Failed to retrieve image from S3: {str(e)}") from e
        except (BotoCoreError, Exception) as e:
            raise StorageError(f"Unexpected error retrieving image: {str(e)}") from e
    
    async def delete_image(
        self,
        user_id: int,
        trip_id: int,
        trip_day_id: int,
        s3_key: str,
    ) -> None:
        """
        Delete an image from S3 storage.
        
        Args:
            user_id: User ID (for validation)
            trip_id: Trip ID (for validation)
            trip_day_id: Trip day ID (for validation)
            s3_key: S3 key/path of the file to delete
            
        Raises:
            ImageNotFoundError: If image doesn't exist
            StorageError: If deletion fails
        """
        # Validate that s3_key matches the expected structure
        expected_prefix = f"{user_id}/{trip_id}/{trip_day_id}/"
        if not s3_key.startswith(expected_prefix):
            raise StorageError(
                f"S3 key {s3_key} does not match expected structure "
                f"for user {user_id}, trip {trip_id}, trip_day {trip_day_id}"
            )
        
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
                region_name=self.region,
            ) as s3:
                await s3.delete_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                )
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchKey':
                raise ImageNotFoundError(f"Image not found: {s3_key}") from e
            raise StorageError(f"Failed to delete image from S3: {str(e)}") from e
        except (BotoCoreError, Exception) as e:
            raise StorageError(f"Unexpected error deleting image: {str(e)}") from e
    
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
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
                region_name=self.region,
            ) as s3:
                url = await s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': s3_key,
                    },
                    ExpiresIn=expiration,
                )
                
                return url
                
        except (ClientError, BotoCoreError, Exception) as e:
            raise StorageError(f"Failed to generate presigned URL: {str(e)}") from e

