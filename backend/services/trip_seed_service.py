"""
Service for managing trip seed conversations with the AI agent.

This service handles the orchestration between:
- Conversation management
- TripSeed state management
- Agent interaction
"""
from typing import Optional, Any
from pydantic import BaseModel, field_validator
from core.models.trips.trip_seed import TripSeed
from core.models.trips.trip_seed_status import TripSeedStatus
from core.models.trips.trip_mode import TripMode
from core.models.trips.budget_band import BudgetBand
from core.models.trips.companions import Companions
from services.core.agent.conversation_service import ConversationService
from services.core.agent.trip_seed_agent_service import (
    TripSeedAgentService,
    TripSeedAgentResponse,
)
from dtos.trip_seed_dto import TripSeedStateResponse


class ProcessMessageResponse(BaseModel):
    """Response model for process_message service method."""
    agent_response: TripSeedAgentResponse
    conversation_id: int
    trip_seed: Any  # Use Any to allow TripSeed ORM objects or mocks in tests
    
    class Config:
        """Pydantic configuration for ORM objects."""
        from_attributes = True
        arbitrary_types_allowed = True


class TripSeedService:
    """Service for managing trip seed conversations."""
    
    def __init__(
        self,
        conversation_service: ConversationService,
        agent_service: TripSeedAgentService,
    ):
        """
        Initialize the Trip Seed Service.
        
        Args:
            conversation_service: Service for managing conversations
            agent_service: Trip Seed Agent service
        """
        self.conversation_service = conversation_service
        self.agent_service = agent_service
    
    async def process_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[int] = None,
    ) -> ProcessMessageResponse:
        """
        Process a user message in a trip seed conversation.
        
        This method:
        1. Creates or retrieves conversation
        2. Creates or retrieves TripSeed (DRAFT status)
        3. Gets current TripSeed state
        4. Calls agent with message and state
        5. Updates TripSeed with extracted data
        6. Updates status if complete
        7. Returns agent response with conversation and trip seed
        
        Args:
            user_id: ID of the user
            message: User's message
            conversation_id: Optional conversation ID (creates new if None)
            
        Returns:
            ProcessMessageResponse with agent response, conversation_id, and trip_seed
        """
        # Get or create conversation
        if conversation_id:
            conversation = await self.conversation_service.get_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found or doesn't belong to user")
        else:
            # Create new conversation
            conversation = await self.conversation_service.create_conversation(
                user_id=user_id,
                agent_name="trip_seed_agent"
            )
        
        # Get existing TripSeed or prepare to create one
        trip_seed = await TripSeed.get_or_none(
            conversation_id=conversation.id,
            status=TripSeedStatus.DRAFT
        )
        
        # Get current TripSeed state (empty dict if doesn't exist yet)
        if trip_seed:
            trip_seed_state = await self._get_trip_seed_state(trip_seed)
        else:
            trip_seed_state = {}
        
        # Process with agent
        agent_response = await self.agent_service.process_with_trip_seed_state(
            user_message=message,
            conversation_id=conversation.id,
            trip_seed_state=trip_seed_state,
            user_id=user_id,
        )
        
        # Get or create TripSeed with initial extracted data
        if not trip_seed:
            # Create TripSeed with extracted data (or defaults if none)
            # Extract enum values if they exist
            trip_mode = agent_response.extracted_data.trip_mode
            budget_band = agent_response.extracted_data.budget_band
            
            initial_data = {
                "num_days": agent_response.extracted_data.num_days,
                "trip_mode": trip_mode.value if trip_mode else None,
                "budget_band": budget_band.value if budget_band else None,
            }
            trip_seed = await self._get_or_create_trip_seed(
                conversation.id,
                initial_data=initial_data
            )
        
        # Update TripSeed with extracted data
        await self._update_trip_seed_from_extracted_data(
            trip_seed=trip_seed,
            extracted_data=agent_response.extracted_data,
            current_state=trip_seed_state
        )
        
        # Update status if complete
        if agent_response.is_complete and trip_seed.status == TripSeedStatus.DRAFT:
            trip_seed.status = TripSeedStatus.COMPLETE
            await trip_seed.save()
        
        return ProcessMessageResponse(
            agent_response=agent_response,
            conversation_id=conversation.id,
            trip_seed=trip_seed,
        )
    
    async def _get_or_create_trip_seed(
        self,
        conversation_id: int,
        initial_data: Optional[dict] = None,
    ) -> TripSeed:
        """
        Get existing DRAFT TripSeed or create a new one.
        
        TripSeed requires num_days, trip_mode, and budget_band, so we only
        create it after we have at least some data from the agent.
        
        Args:
            conversation_id: ID of the conversation
            initial_data: Optional dict with initial data to populate
            
        Returns:
            TripSeed object (DRAFT status)
        """
        # Try to find existing DRAFT TripSeed for this conversation
        trip_seed = await TripSeed.get_or_none(
            conversation_id=conversation_id,
            status=TripSeedStatus.DRAFT
        )
        
        if trip_seed:
            return trip_seed
        
        # If we have initial data, use it; otherwise use defaults
        # Note: These fields are required, so we use defaults that will be updated
        num_days = initial_data.get("num_days") if initial_data else 1
        trip_mode = initial_data.get("trip_mode") if initial_data else TripMode.LOCAL_HUB
        budget_band = initial_data.get("budget_band") if initial_data else BudgetBand.COMFORTABLE
        
        # Convert string enums to enum objects if needed
        if isinstance(trip_mode, str):
            trip_mode = TripMode(trip_mode)
        if isinstance(budget_band, str):
            budget_band = BudgetBand(budget_band)
        
        # Create new TripSeed
        trip_seed = await TripSeed.create(
            conversation_id=conversation_id,
            num_days=num_days or 1,
            trip_mode=trip_mode or TripMode.LOCAL_HUB,
            budget_band=budget_band or BudgetBand.COMFORTABLE,
            status=TripSeedStatus.DRAFT
        )
        
        return trip_seed
    
    async def _get_trip_seed_state(self, trip_seed: TripSeed) -> dict:
        """
        Get current TripSeed state as a dictionary.
        
        Args:
            trip_seed: TripSeed object
            
        Returns:
            Dict with TripSeed field values (None for missing/unset)
        """
        # Check if values are "real" or just defaults
        # We consider 0 or 1 as potentially unset for num_days
        # For enums, we check if they're the defaults
        
        num_days = trip_seed.num_days
        # If num_days is 0 or 1 and we don't have other data, consider it unset
        # This is a heuristic - in practice, the agent will set real values
        
        return {
            "num_days": num_days if num_days and num_days > 0 else None,
            "trip_mode": trip_seed.trip_mode.value if trip_seed.trip_mode else None,
            "budget_band": trip_seed.budget_band.value if trip_seed.budget_band else None,
            "start_location_text": trip_seed.start_location_text,
            "start_latitude": float(trip_seed.start_latitude) if trip_seed.start_latitude else None,
            "start_longitude": float(trip_seed.start_longitude) if trip_seed.start_longitude else None,
            "companions": trip_seed.companions.value if trip_seed.companions else None,
        }
    
    async def _update_trip_seed_from_extracted_data(
        self,
        trip_seed: TripSeed,
        extracted_data,
        current_state: dict,
    ):
        """
        Update TripSeed with extracted data from agent.
        
        Only updates fields that were actually extracted (not None).
        
        Args:
            trip_seed: TripSeed object to update
            extracted_data: TripSeedExtractedData from agent
            current_state: Current state dict (for merging logic)
        """
        # Update num_days if extracted
        if extracted_data.num_days is not None:
            trip_seed.num_days = extracted_data.num_days
        
        # Update trip_mode if extracted
        if extracted_data.trip_mode is not None:
            trip_seed.trip_mode = extracted_data.trip_mode
        
        # Update budget_band if extracted
        if extracted_data.budget_band is not None:
            trip_seed.budget_band = extracted_data.budget_band
        
        # Update start_location_text if extracted
        if extracted_data.start_location_text is not None:
            trip_seed.start_location_text = extracted_data.start_location_text
        
        # Update coordinates if extracted
        if extracted_data.start_latitude is not None:
            trip_seed.start_latitude = extracted_data.start_latitude
        if extracted_data.start_longitude is not None:
            trip_seed.start_longitude = extracted_data.start_longitude
        
        # Update companions if extracted
        if extracted_data.companions is not None:
            trip_seed.companions = extracted_data.companions
        
        await trip_seed.save()
    
    async def get_trip_seed_state_response(
        self,
        trip_seed: TripSeed,
    ) -> TripSeedStateResponse:
        """
        Convert TripSeed to TripSeedStateResponse DTO.
        
        Args:
            trip_seed: TripSeed object
            
        Returns:
            TripSeedStateResponse DTO
        """
        state = await self._get_trip_seed_state(trip_seed)
        
        # Check if complete
        is_complete = (
            state["num_days"] is not None and
            state["trip_mode"] is not None and
            state["budget_band"] is not None
        )
        
        # Get missing fields
        missing_fields = []
        if state["num_days"] is None:
            missing_fields.append("num_days")
        if state["trip_mode"] is None:
            missing_fields.append("trip_mode")
        if state["budget_band"] is None:
            missing_fields.append("budget_band")
        
        return TripSeedStateResponse(
            trip_seed_id=trip_seed.id,
            conversation_id=trip_seed.conversation_id,
            num_days=state["num_days"],
            trip_mode=state["trip_mode"],
            budget_band=state["budget_band"],
            start_location_text=state["start_location_text"],
            companions=state["companions"],
            status=trip_seed.status.value,
            is_complete=is_complete,
            missing_fields=missing_fields,
        )

