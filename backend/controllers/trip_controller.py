"""Trip controller for listing trips and active trip seeds."""
from fastapi import APIRouter, Depends
from core.dependencies import CurrentUser
from core.models.user import User
from dtos.trip_dto import TripsListResponse
from services.trip_service import TripService
from services.trip_seed_service import TripSeedService
from services.core.agent.conversation_service import ConversationService
from services.core.agent.trip_seed_agent_service import TripSeedAgentService

router = APIRouter(prefix="/api/trips", tags=["trips"])


def get_trip_service() -> TripService:
    """
    Dependency to get TripService instance.
    
    Creates services with proper dependencies.
    """
    conversation_service = ConversationService()
    agent_service = TripSeedAgentService(
        conversation_service=conversation_service
    )
    trip_seed_service = TripSeedService(
        conversation_service=conversation_service,
        agent_service=agent_service,
    )
    return TripService(trip_seed_service=trip_seed_service)


@router.get("", response_model=TripsListResponse)
async def get_trips(
    user: CurrentUser,
    trip_service: TripService = Depends(get_trip_service),
) -> TripsListResponse:
    """
    Get all trips and active trip seeds for the current user.
    
    Returns:
    - trips: List of completed/saved trips
    - active_trip_seeds: List of in-progress trip planning conversations
    
    Args:
        user: Current authenticated user (from dependency)
        trip_service: Trip service (from dependency)
        
    Returns:
        TripsListResponse with trips and active trip seeds
    """
    return await trip_service.get_user_trips_and_active_seeds(user_id=user.id)

