# Tests

## Running Tests

### Prerequisites

1. **Environment Variables**: Set up your `.env` file with:
   - `WATSONX_APIKEY` - IBM WatsonX API key (required - real API is used)
   - `WATSONX_PROJECT_ID` - IBM WatsonX project ID (required - real API is used)
   - `WATSONX_URL` - IBM WatsonX service URL (required - real API is used)
   
   **Note**: Database operations are mocked - no database setup or migrations needed!

### Run All Tests

```bash
cd backend
poetry run pytest
```

### Run Specific Test

```bash
poetry run pytest tests/test_trip_seed_conversation.py
```

### Run with Verbose Output

```bash
poetry run pytest -v -s tests/test_trip_seed_conversation.py
```

The `-s` flag shows print statements (useful for seeing the conversation flow).

## Test Structure

- `conftest.py`: Shared fixtures for WatsonX credentials
- `test_trip_seed_conversation.py`: Integration test for multi-turn trip seed conversations

## Notes

- Tests use the **real IBM WatsonX API** (not mocked) - this is the only external service that's real
- Database operations are **fully mocked** - no database setup, migrations, or cleanup needed
- Tests require valid WatsonX credentials (test will skip if not provided)
- All database models (User, Conversation, TripSeed, Message) are mocked using `unittest.mock`

