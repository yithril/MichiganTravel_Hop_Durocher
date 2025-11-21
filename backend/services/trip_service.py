"""
Service for managing trips and active trip seeds.

This service handles:
- Fetching completed trips for a user
- Fetching active trip seeds (in-progress conversations)
"""
from typing import List
from core.models.trips.trip import Trip
from core.models.trips.trip_seed import TripSeed
from core.models.trips.trip_seed_status import TripSeedStatus
from core.models.conversation import Conversation
from dtos.trip_dto import TripResponse, ActiveTripSeedResponse, TripsListResponse
from services.trip_seed_service import TripSeedService


class TripService:
    """Service for managing trips and active trip seeds."""
    
    def __init__(self, trip_seed_service: TripSeedService):
        """
        Initialize the Trip Service.
        
        Args:
            trip_seed_service: Trip seed service for state conversion
        """
        self.trip_seed_service = trip_seed_service
    
    async def get_user_trips_and_active_seeds(
        self,
        user_id: int,
    ) -> TripsListResponse:
        """
        Get all trips and active trip seeds for a user.
        
        Returns:
        - Completed trips (saved trips)
        - Active trip seeds (DRAFT or COMPLETE status conversations)
        
        Args:
            user_id: ID of the user
            
        Returns:
            TripsListResponse with trips and active trip seeds
        """
        # Get all completed trips for the user
        trips = await Trip.filter(user_id=user_id).order_by('-created_at')
        
        # Get all active trip seeds (DRAFT or COMPLETE) for the user
        # Active trip seeds are those with conversations belonging to the user
        # Use a join query to get trip seeds with their conversations
        active_trip_seeds_raw = await TripSeed.filter(
            conversation__user_id=user_id,
            conversation__agent_name="trip_seed_agent",
            status__in=[TripSeedStatus.DRAFT, TripSeedStatus.COMPLETE]
        ).prefetch_related('conversation').order_by('-updated_at')
        
        active_trip_seeds = []
        for trip_seed in active_trip_seeds_raw:
            # Convert to DTO
            trip_seed_state = await self.trip_seed_service.get_trip_seed_state_response(
                trip_seed
            )
            
            active_trip_seeds.append(
                ActiveTripSeedResponse(
                    trip_seed_id=trip_seed.id,
                    conversation_id=trip_seed.conversation_id,
                    status=trip_seed.status.value,
                    num_days=trip_seed_state.num_days,
                    trip_mode=trip_seed_state.trip_mode,
                    budget_band=trip_seed_state.budget_band,
                    start_location_text=trip_seed_state.start_location_text,
                    companions=trip_seed_state.companions,
                    is_complete=trip_seed_state.is_complete,
                    missing_fields=trip_seed_state.missing_fields,
                    updated_at=trip_seed.updated_at.isoformat(),
                )
            )
        
        # Convert trips to DTOs
        trip_responses = [
            TripResponse(
                id=trip.id,
                name=trip.name,
                user_id=trip.user_id,
                start_location_text=trip.start_location_text,
                start_latitude=float(trip.start_latitude) if trip.start_latitude else None,
                start_longitude=float(trip.start_longitude) if trip.start_longitude else None,
                num_days=trip.num_days,
                trip_mode=trip.trip_mode.value,
                budget_band=trip.budget_band.value,
                companions=trip.companions.value if trip.companions else None,
                created_at=trip.created_at.isoformat(),
                updated_at=trip.updated_at.isoformat(),
            )
            for trip in trips
        ]
        
        return TripsListResponse(
            trips=trip_responses,
            active_trip_seeds=active_trip_seeds,
            total_trips=len(trip_responses),
            total_active=len(active_trip_seeds),
        )

