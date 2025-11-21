"""
Integration test for multi-turn trip seed conversation.

This test simulates a complete happy path conversation where:
1. User starts planning a trip
2. Agent asks questions and collects information
3. After all required fields are collected, TripSeed is complete

Uses real IBM WatsonX API (not mocked).
Database operations are mocked to avoid storing data in actual database.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.trip_seed_service import TripSeedService
from services.core.agent.conversation_service import ConversationService
from services.core.agent.trip_seed_agent_service import TripSeedAgentService
from core.models.trips.trip_seed import TripSeed
from core.models.trips.trip_seed_status import TripSeedStatus


@pytest.mark.asyncio
async def test_multi_turn_trip_seed_conversation(watsonx_credentials):
    """
    Test a complete multi-turn conversation for trip planning.
    
    Happy path: User and agent have a conversation, agent collects all required info,
    and TripSeed becomes complete.
    
    Database operations are mocked - only IBM WatsonX API is real.
    """
    # Mock user
    mock_user = MagicMock()
    mock_user.id = 1
    
    # Mock conversation
    mock_conversation = MagicMock()
    mock_conversation.id = 1
    mock_conversation.user_id = mock_user.id
    
    # Mock TripSeed
    mock_trip_seed = MagicMock()
    mock_trip_seed.id = 1
    mock_trip_seed.conversation_id = mock_conversation.id
    mock_trip_seed.status = TripSeedStatus.DRAFT
    mock_trip_seed.save = AsyncMock(return_value=None)
    
    # Track state
    trip_seed_state = {"num_days": None, "trip_mode": None, "budget_band": None}
    
    # Mock all database operations
    with patch.object(ConversationService, 'create_conversation', new_callable=AsyncMock) as mock_create_conv, \
         patch.object(ConversationService, 'get_conversation', new_callable=AsyncMock) as mock_get_conv, \
         patch.object(ConversationService, 'add_message', new_callable=AsyncMock), \
         patch.object(ConversationService, 'get_conversation_messages', new_callable=AsyncMock) as mock_get_msgs, \
         patch.object(TripSeed, 'get_or_none', new_callable=AsyncMock) as mock_get_trip_seed, \
         patch.object(TripSeed, 'create', new_callable=AsyncMock) as mock_create_trip_seed:
        
        # Set up mocks
        mock_create_conv.return_value = mock_conversation
        mock_get_conv.return_value = mock_conversation
        mock_get_msgs.return_value = []
        mock_create_trip_seed.return_value = mock_trip_seed
        
        # get_or_none: first call returns None, then returns mock
        call_count = [0]
        def get_trip_seed_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return None
            # Update mock state
            mock_trip_seed.num_days = trip_seed_state.get("num_days")
            mock_trip_seed.trip_mode = trip_seed_state.get("trip_mode")
            mock_trip_seed.budget_band = trip_seed_state.get("budget_band")
            return mock_trip_seed
        
        mock_get_trip_seed.side_effect = get_trip_seed_side_effect
        
        # Set up services with real IBM API
        conversation_service = ConversationService()
        agent_service = TripSeedAgentService(
            api_key=watsonx_credentials["api_key"],
            project_id=watsonx_credentials["project_id"],
            url=watsonx_credentials["url"],
            conversation_service=conversation_service,
        )
        trip_seed_service = TripSeedService(
            conversation_service=conversation_service,
            agent_service=agent_service,
        )
        
        conversation_id = None
        result = None
        max_turns = 6
        turn_count = 0
        
        # Conversation flow
        messages = [
            "I want to plan a trip",
            "I want a 3-day road trip from Detroit",
            "I'd say comfortable, mid-range budget",
        ]
        
        # Process messages until complete
        for message in messages:
            turn_count += 1
            print(f"\n=== Turn {turn_count}: {message} ===")
            
            result = await trip_seed_service.process_message(
                user_id=mock_user.id,
                message=message,
                conversation_id=conversation_id,
            )
            
            conversation_id = result.conversation_id
            
            print(f"Agent: {result.agent_response.response_text[:100]}...")
            print(f"Complete: {result.agent_response.is_complete}")
            
            # Update state from extracted data
            extracted = result.agent_response.extracted_data
            if extracted.num_days:
                trip_seed_state["num_days"] = extracted.num_days
            if extracted.trip_mode:
                trip_seed_state["trip_mode"] = extracted.trip_mode
            if extracted.budget_band:
                trip_seed_state["budget_band"] = extracted.budget_band
            
            # If complete, we're done
            if result.agent_response.is_complete:
                break
        
        # If not complete yet, continue with follow-up messages
        while not result.agent_response.is_complete and turn_count < max_turns:
            turn_count += 1
            print(f"\n=== Turn {turn_count}: Continuing ===")
            
            # Provide missing info based on what's needed
            if result.agent_response.missing_fields:
                missing = result.agent_response.missing_fields[0]
                if missing == "budget_band":
                    message = "comfortable budget"
                elif missing == "num_days":
                    message = "3 days"
                elif missing == "trip_mode":
                    message = "road trip"
                else:
                    message = "comfortable budget for a 3-day road trip"
            else:
                message = "yes, that's correct"
            
            result = await trip_seed_service.process_message(
                user_id=mock_user.id,
                message=message,
                conversation_id=conversation_id,
            )
            
            print(f"Agent: {result.agent_response.response_text[:100]}...")
            print(f"Complete: {result.agent_response.is_complete}")
            
            # Update state
            extracted = result.agent_response.extracted_data
            if extracted.num_days:
                trip_seed_state["num_days"] = extracted.num_days
            if extracted.trip_mode:
                trip_seed_state["trip_mode"] = extracted.trip_mode
            if extracted.budget_band:
                trip_seed_state["budget_band"] = extracted.budget_band
        
        # Final assertions - just verify it's complete
        assert result.agent_response.is_complete, f"TripSeed should be complete after {turn_count} turns"
        assert result.trip_seed.status == TripSeedStatus.COMPLETE
        
        print(f"\n✅ Test passed! TripSeed is complete after {turn_count} turns")
        print(f"   Final state: {trip_seed_state}")
