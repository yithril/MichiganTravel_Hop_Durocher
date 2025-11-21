"""Trip Seed Agent controller for handling trip planning conversations."""
from fastapi import APIRouter, HTTPException, status, Depends
from dtos.trip_seed_dto import (
    TripSeedMessageRequest,
    TripSeedAgentResponse as TripSeedAgentResponseDTO,
    TripSeedStateResponse,
)
from dtos.agent_dto import ConversationResponse
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


def get_conversation_service() -> ConversationService:
    """
    Dependency to get ConversationService instance.
    """
    return ConversationService()


@router.post("/message", response_model=TripSeedAgentResponseDTO)
async def send_message(
    request: TripSeedMessageRequest,
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
        trip_seed_service: Trip seed service (from dependency)
        
    Returns:
        TripSeedAgentResponseDTO with agent response and trip seed state
        
    Raises:
        HTTPException 400: If conversation not found or validation fails
    """
    try:
        # TODO: Re-add authentication
        # Process message through service
        result = await trip_seed_service.process_message(
            user_id=1,
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
            is_complete=trip_seed_state.is_complete,  # Use the calculated state, not agent's guess
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


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    """
    Get a conversation with its messages by conversation ID.
    
    This endpoint:
    - Retrieves the conversation and all its messages
    - Validates that the conversation belongs to the current user
    - Returns conversation with messages in chronological order
    
    Args:
        conversation_id: ID of the conversation to retrieve
        conversation_service: Conversation service (from dependency)
        
    Returns:
        ConversationResponse with messages
        
    Raises:
        HTTPException 400: If conversation not found or doesn't belong to user
    """
    try:
        # TODO: Re-add authentication
        # Get conversation and validate it belongs to user
        conversation = await conversation_service.get_conversation(
            conversation_id=conversation_id,
            user_id=1,
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Get conversation with messages
        return await conversation_service.get_conversation_response(conversation_id)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> dict:
    """
    Delete a conversation and all its messages.
    
    This endpoint:
    - Validates that the conversation belongs to the current user
    - Deletes the conversation and all associated messages
    - Returns success status
    
    Args:
        conversation_id: ID of the conversation to delete
        conversation_service: Conversation service (from dependency)
        
    Returns:
        Dict with success status
        
    Raises:
        HTTPException 404: If conversation not found
        HTTPException 400: If conversation doesn't belong to user
    """
    try:
        # TODO: Re-add authentication
        # Delete conversation (validates it belongs to user)
        deleted = await conversation_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=1,
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {"success": True, "message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )

