"""
Tortoise ORM configuration for Aerich migrations.

This is separate from core.config to avoid circular dependencies
and .env loading issues during migration operations.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/appdb")

TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["core.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

