"""Trip Seed Agent controller for handling trip planning conversations."""
from fastapi import APIRouter, HTTPException, status, Depends
from core.dependencies import CurrentUser
from core.models.user import User
from dtos.trip_seed_dto import (
    TripSeedMessageRequest,
    TripSeedAgentResponse as TripSeedAgentResponseDTO,
    TripSeedStateResponse,
)
from services.trip_seed_service import TripSeedService
from services.core.agent.conversation_service import ConversationService
from services.core.agent.trip_seed_agent_service import TripSeedAgentService

router = APIRouter(prefix="/api/trip-seed", tags=["trip-seed"])


def get_trip_seed_service() -> TripSeedService:
    """
    Dependency to get TripSeedService instance.
    
    Creates services with proper dependencies.
    """
    conversation_service = ConversationService()
    agent_service = TripSeedAgentService(
        conversation_service=conversation_service
    )
    return TripSeedService(
        conversation_service=conversation_service,
        agent_service=agent_service,
    )


@router.post("/message", response_model=TripSeedAgentResponseDTO)
async def send_message(
    request: TripSeedMessageRequest,
    user: CurrentUser,
    trip_seed_service: TripSeedService = Depends(get_trip_seed_service),
) -> TripSeedAgentResponseDTO:
    """
    Send a message to the trip seed agent.
    
    This endpoint:
    - Creates or continues a conversation
    - Processes the message with the agent
    - Updates TripSeed state
    - Returns agent response and current state
    
    Args:
        request: Message request with user message and optional conversation_id
        user: Current authenticated user (from dependency)
        trip_seed_service: Trip seed service (from dependency)
        
    Returns:
        TripSeedAgentResponseDTO with agent response and trip seed state
        
    Raises:
        HTTPException 400: If conversation not found or validation fails
        HTTPException 401: If not authenticated (handled by CurrentUser dependency)
    """
    try:
        # Process message through service
        result = await trip_seed_service.process_message(
            user_id=user.id,
            message=request.message,
            conversation_id=request.conversation_id,
        )
        
        # Get state response
        trip_seed_state = await trip_seed_service.get_trip_seed_state_response(
            result.trip_seed
        )
        
        return TripSeedAgentResponseDTO(
            response_text=result.agent_response.response_text,
            conversation_id=result.conversation_id,
            trip_seed_state=trip_seed_state,
            is_complete=result.agent_response.is_complete,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

