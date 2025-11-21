"""
Service for managing trips and active trip seeds.

This service handles:
- Fetching completed trips for a user
- Fetching active trip seeds (in-progress conversations)
- Creating trips from trip seeds
- Getting trip details with days and stops
"""
from typing import List
from core.models.trips.trip import Trip
from core.models.trips.trip_seed import TripSeed
from core.models.trips.trip_seed_status import TripSeedStatus
from core.models.trips.trip_status import TripStatus
from core.models.trips.trip_seed_vibe import TripSeedVibe
from core.models.trips.trip_vibe import TripVibe
from core.models.trips.trip_day import TripDay
from core.models.conversation import Conversation
from dtos.trip_dto import (
    TripResponse,
    ActiveTripSeedResponse,
    TripsListResponse,
    CreateTripRequest,
    TripDetailsResponse,
)
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
                status=trip.status.value,
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
    
    async def create_trip_from_seed(
        self,
        user_id: int,
        request: CreateTripRequest,
    ) -> TripResponse:
        """
        Create a Trip from a completed TripSeed.
        
        Args:
            user_id: ID of the user creating the trip
            request: CreateTripRequest with trip_seed_id and name
            
        Returns:
            TripResponse for the newly created trip
            
        Raises:
            ValueError: If trip seed not found, not complete, or doesn't belong to user
        """
        # Get the trip seed and verify it belongs to the user
        trip_seed = await TripSeed.filter(
            id=request.trip_seed_id,
            conversation__user_id=user_id
        ).prefetch_related('conversation').first()
        
        if not trip_seed:
            raise ValueError(f"Trip seed {request.trip_seed_id} not found or doesn't belong to user")
        
        # Verify trip seed is COMPLETE
        if trip_seed.status != TripSeedStatus.COMPLETE:
            raise ValueError(f"Trip seed {request.trip_seed_id} must be COMPLETE to create a trip. Current status: {trip_seed.status.value}")
        
        # Create the Trip from TripSeed data with PLANNED status
        trip = await Trip.create(
            user_id=user_id,
            name=request.name,
            start_location_text=trip_seed.start_location_text,
            start_latitude=trip_seed.start_latitude,
            start_longitude=trip_seed.start_longitude,
            num_days=trip_seed.num_days,
            trip_mode=trip_seed.trip_mode,
            budget_band=trip_seed.budget_band,
            companions=trip_seed.companions,
            status=TripStatus.PLANNED,
        )
        
        # Copy vibes from TripSeed to Trip
        trip_seed_vibes = await TripSeedVibe.filter(trip_seed_id=trip_seed.id).all()
        for trip_seed_vibe in trip_seed_vibes:
            await TripVibe.create(
                trip_id=trip.id,
                vibe_id=trip_seed_vibe.vibe_id,
                strength=trip_seed_vibe.strength,
            )
        
        # Update TripSeed status to FINALIZED and link to trip
        trip_seed.status = TripSeedStatus.FINALIZED
        trip_seed.trip_id = trip.id
        await trip_seed.save()
        
        # Return TripResponse
        return TripResponse(
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
            status=trip.status.value,
            created_at=trip.created_at.isoformat(),
            updated_at=trip.updated_at.isoformat(),
        )
    
    async def get_trip_details(
        self,
        user_id: int,
        trip_id: int,
    ) -> TripDetailsResponse:
        """
        Get full trip details with days and stops.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            
        Returns:
            TripDetailsResponse with nested days and stops
            
        Raises:
            ValueError: If trip not found or doesn't belong to user
        """
        # Import here to avoid circular dependency
        from dtos.trip_day_dto import TripDayResponse
        from dtos.trip_stop_dto import TripStopResponse
        from core.models.trips.trip_day import TripDay
        from core.models.trips.trip_stop import TripStop
        
        # Get trip and verify it belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Get all days for this trip with their stops
        days = await TripDay.filter(trip_id=trip_id).prefetch_related(
            'base_city',
            'stops__attraction'
        ).order_by('day_index')
        
        # Build day responses with nested stops
        day_responses = []
        for day in days:
            # Get stops for this day
            stops = await TripStop.filter(trip_day_id=day.id).prefetch_related(
                'attraction'
            ).order_by('order_index')
            
            # Build stop responses
            stop_responses = []
            for stop in stops:
                stop_responses.append(
                    TripStopResponse(
                        id=stop.id,
                        trip_day_id=stop.trip_day_id,
                        attraction_id=stop.attraction_id,
                        attraction_name=stop.attraction.name if stop.attraction else None,
                        attraction_type=stop.attraction.type if stop.attraction else None,
                        label=stop.label,
                        slot=stop.slot.value,
                        order_index=stop.order_index,
                        created_at=stop.created_at.isoformat(),
                        updated_at=stop.updated_at.isoformat(),
                    )
                )
            
            day_responses.append(
                TripDayResponse(
                    id=day.id,
                    trip_id=day.trip_id,
                    day_index=day.day_index,
                    base_city_id=day.base_city_id,
                    base_city_name=day.base_city.name if day.base_city else None,
                    notes=day.notes,
                    stops=stop_responses,
                    created_at=day.created_at.isoformat(),
                    updated_at=day.updated_at.isoformat(),
                )
            )
        
        # Return trip details response
        return TripDetailsResponse(
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
            status=trip.status.value,
            days=day_responses,
            created_at=trip.created_at.isoformat(),
            updated_at=trip.updated_at.isoformat(),
        )
    
    async def finalize_trip(
        self,
        user_id: int,
        trip_id: int,
    ) -> TripResponse:
        """
        Finalize a trip when all days have at least one activity.
        
        This validates that:
        - Trip exists and belongs to user
        - Trip is in PLANNED status
        - All days have at least one stop/activity
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip to finalize
            
        Returns:
            TripResponse for the finalized trip
            
        Raises:
            ValueError: If trip not found, doesn't belong to user, not in PLANNED status, or days are incomplete
        """
        from core.models.trips.trip_stop import TripStop
        
        # Get trip and verify it belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Verify trip is in PLANNED status
        if trip.status != TripStatus.PLANNED:
            raise ValueError(f"Trip {trip_id} must be in PLANNED status to finalize. Current status: {trip.status.value}")
        
        # Get all days for this trip
        days = await TripDay.filter(trip_id=trip_id).all()
        
        if not days:
            raise ValueError(f"Trip {trip_id} has no days. Add at least one day before finalizing.")
        
        # Verify each day has at least one stop
        for day in days:
            stop_count = await TripStop.filter(trip_day_id=day.id).count()
            if stop_count == 0:
                raise ValueError(f"Day {day.day_index} has no activities. Each day must have at least one activity to finalize.")
        
        # Trip is valid - status remains PLANNED (finalization is just validation)
        # The trip is ready to go, but status stays PLANNED until user marks it as COMPLETED
        
        # Return updated trip response
        return TripResponse(
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
            status=trip.status.value,
            created_at=trip.created_at.isoformat(),
            updated_at=trip.updated_at.isoformat(),
        )
    
    async def mark_trip_completed(
        self,
        user_id: int,
        trip_id: int,
    ) -> TripResponse:
        """
        Mark a trip as completed (user has gone on the trip).
        
        This allows future features like uploading photos, reviews, etc.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip to mark as completed
            
        Returns:
            TripResponse for the completed trip
            
        Raises:
            ValueError: If trip not found or doesn't belong to user
        """
        # Get trip and verify it belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Update status to COMPLETED
        trip.status = TripStatus.COMPLETED
        await trip.save()
        
        # Return updated trip response
        return TripResponse(
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
            status=trip.status.value,
            created_at=trip.created_at.isoformat(),
            updated_at=trip.updated_at.isoformat(),
        )

