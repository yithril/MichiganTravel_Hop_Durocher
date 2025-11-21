"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # Authentication (NextAuth)
    auth_secret: str = Field(..., alias="AUTH_SECRET")
    auth_url: str = Field(default="http://localhost:8000", alias="AUTH_URL")
    
    # Application
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # IBM WatsonX (optional)
    watsonx_apikey: str | None = Field(default=None, alias="WATSONX_APIKEY")
    watsonx_project_id: str | None = Field(default=None, alias="WATSONX_PROJECT_ID")
    watsonx_url: str | None = Field(default=None, alias="WATSONX_URL")
    watsonx_model_id: str | None = Field(default="ibm/granite-3-8b-instruct", alias="WATSONX_MODEL_ID")
    
    # S3/Object Storage (S3-compatible: MinIO for local, IBM Cloud Object Storage for production)
    s3_endpoint: str | None = Field(default=None, alias="S3_ENDPOINT")
    s3_access_key: str | None = Field(default=None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, alias="S3_SECRET_KEY")
    s3_bucket_name: str | None = Field(default=None, alias="S3_BUCKET_NAME")
    s3_use_ssl: bool = Field(default=True, alias="S3_USE_SSL")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables
        case_sensitive = False


# Singleton instance
settings = Settings()

