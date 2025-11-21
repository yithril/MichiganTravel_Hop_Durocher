"""
Pytest configuration and shared fixtures for tests.

Note: Database operations are mocked in tests to avoid storing data.
Only IBM WatsonX API calls are real.
"""
import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL from environment or use default."""
    # Use the same database URL as main app, but you can override with TEST_DATABASE_URL
    return os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/appdb")


@pytest.fixture(scope="session")
async def setup_test_database(test_database_url):
    """
    Set up test database connection.
    
    Note: This assumes the database schema is already created via migrations.
    For a fresh test database, you would run: aerich upgrade
    """
    await Tortoise.init(
        db_url=test_database_url,
        modules={"models": ["core.models", "aerich.models"]}
    )
    
    yield
    
    # Cleanup
    await connections.close_all()


@pytest.fixture(scope="function", autouse=True)
async def db_cleanup(setup_test_database):
    """
    Clean up database after each test.
    
    This deletes all data but keeps the schema.
    For transaction-based rollback, you'd need to use a different approach.
    """
    yield
    
    # Clean up all test data
    from core.models.conversation import Conversation, Message
    from core.models.trips.trip_seed import TripSeed
    
    # Delete in reverse order of dependencies
    await TripSeed.all().delete()
    await Message.all().delete()
    await Conversation.all().delete()
    await User.filter(email="test@example.com").delete()


@pytest.fixture
async def test_user(db_transaction):
    """Create a test user for tests."""
    user = await User.create(
        email="test@example.com",
        password_hash="hashed_password",  # Not used in these tests
        full_name="Test User",
        is_active=True
    )
    return user


@pytest.fixture
def watsonx_credentials():
    """
    Get WatsonX credentials from environment.
    
    Fails fast if credentials are missing (does not skip).
    """
    api_key = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    url = os.getenv("WATSONX_URL")
    
    if not api_key:
        raise ValueError(
            "WATSONX_APIKEY environment variable is required. "
            "Set it in your .env file or environment."
        )
    if not project_id:
        raise ValueError(
            "WATSONX_PROJECT_ID environment variable is required. "
            "Set it in your .env file or environment."
        )
    if not url:
        raise ValueError(
            "WATSONX_URL environment variable is required. "
            "Set it in your .env file or environment."
        )
    
    return {
        "api_key": api_key,
        "project_id": project_id,
        "url": url,
    }

