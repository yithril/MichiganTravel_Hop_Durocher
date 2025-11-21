"""Trip controller for listing trips and active trip seeds."""
from fastapi import APIRouter, Depends, HTTPException, status
from dtos.trip_dto import (
    TripsListResponse,
    CreateTripRequest,
    TripResponse,
    TripDetailsResponse,
)
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
    trip_service: TripService = Depends(get_trip_service),
) -> TripsListResponse:
    """
    Get all trips and active trip seeds for the current user.
    
    Returns:
    - trips: List of completed/saved trips
    - active_trip_seeds: List of in-progress trip planning conversations
    
    Args:
        trip_service: Trip service (from dependency)
        
    Returns:
        TripsListResponse with trips and active trip seeds
    """
    # TODO: Re-add authentication
    return await trip_service.get_user_trips_and_active_seeds(user_id=1)


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    request: CreateTripRequest,
    trip_service: TripService = Depends(get_trip_service),
) -> TripResponse:
    """
    Create a trip from a completed trip seed.
    
    Args:
        request: CreateTripRequest with trip_seed_id and name
        trip_service: Trip service (from dependency)
        
    Returns:
        TripResponse for the newly created trip
        
    Raises:
        HTTPException 400: If trip seed not found, not complete, or doesn't belong to user
    """
    try:
        # TODO: Re-add authentication
        return await trip_service.create_trip_from_seed(
            user_id=1,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{trip_id}", response_model=TripDetailsResponse)
async def get_trip_details(
    trip_id: int,
    trip_service: TripService = Depends(get_trip_service),
) -> TripDetailsResponse:
    """
    Get full trip details with days and stops.
    
    Args:
        trip_id: ID of the trip
        trip_service: Trip service (from dependency)
        
    Returns:
        TripDetailsResponse with nested days and stops
        
    Raises:
        HTTPException 400: If trip not found or doesn't belong to user
    """
    try:
        # TODO: Re-add authentication
        return await trip_service.get_trip_details(
            user_id=1,
            trip_id=trip_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{trip_id}/finalize", response_model=TripResponse)
async def finalize_trip(
    trip_id: int,
    trip_service: TripService = Depends(get_trip_service),
) -> TripResponse:
    """
    Finalize a trip when all days have at least one activity.
    
    Validates that:
    - Trip exists and belongs to user
    - Trip is in PLANNED status
    - All days have at least one stop/activity
    
    Args:
        trip_id: ID of the trip to finalize
        user: Current authenticated user (from dependency)
        trip_service: Trip service (from dependency)
        
    Returns:
        TripResponse for the finalized trip
        
    Raises:
        HTTPException 400: If trip not found, doesn't belong to user, not in PLANNED status, or days are incomplete
    """
    try:
        # TODO: Re-add authentication
        return await trip_service.finalize_trip(
            user_id=1,
            trip_id=trip_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{trip_id}/complete", response_model=TripResponse)
async def mark_trip_completed(
    trip_id: int,
    trip_service: TripService = Depends(get_trip_service),
) -> TripResponse:
    """
    Mark a trip as completed (user has gone on the trip).
    
    This allows future features like uploading photos, reviews, etc.
    
    Args:
        trip_id: ID of the trip to mark as completed
        user: Current authenticated user (from dependency)
        trip_service: Trip service (from dependency)
        
    Returns:
        TripResponse for the completed trip
        
    Raises:
        HTTPException 400: If trip not found or doesn't belong to user
    """
    try:
        # TODO: Re-add authentication
        return await trip_service.mark_trip_completed(
            user_id=1,
            trip_id=trip_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

