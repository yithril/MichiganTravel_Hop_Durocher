"""
Service for managing trip days.

This service handles CRUD operations for TripDays.
"""
from typing import List
from core.models.trips.trip import Trip
from core.models.trips.trip_day import TripDay
from core.models.places.city import City
from dtos.trip_day_dto import (
    TripDayResponse,
    CreateTripDayRequest,
    UpdateTripDayRequest,
)
from dtos.trip_stop_dto import TripStopResponse


class TripDayService:
    """Service for managing trip days."""
    
    async def get_trip_days(
        self,
        user_id: int,
        trip_id: int,
    ) -> List[TripDayResponse]:
        """
        Get all days for a trip.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            
        Returns:
            List of TripDayResponse objects
            
        Raises:
            ValueError: If trip not found or doesn't belong to user
        """
        # Verify trip belongs to user
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
            from core.models.trips.trip_stop import TripStop
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
        
        return day_responses
    
    async def create_trip_day(
        self,
        user_id: int,
        trip_id: int,
        request: CreateTripDayRequest,
    ) -> TripDayResponse:
        """
        Create a new day for a trip.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            request: CreateTripDayRequest with day_index, base_city_id, and notes
            
        Returns:
            TripDayResponse for the newly created day
            
        Raises:
            ValueError: If trip not found, doesn't belong to user, or day_index already exists
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Check if day_index already exists for this trip
        existing_day = await TripDay.filter(
            trip_id=trip_id,
            day_index=request.day_index
        ).first()
        
        if existing_day:
            raise ValueError(f"Day {request.day_index} already exists for trip {trip_id}")
        
        # Verify base_city_id if provided
        if request.base_city_id:
            city = await City.filter(id=request.base_city_id).first()
            if not city:
                raise ValueError(f"City {request.base_city_id} not found")
        
        # Create the day
        day = await TripDay.create(
            trip_id=trip_id,
            day_index=request.day_index,
            base_city_id=request.base_city_id,
            notes=request.notes,
        )
        
        # Reload with relations
        await day.fetch_related('base_city')
        
        # Return response (no stops yet)
        return TripDayResponse(
            id=day.id,
            trip_id=day.trip_id,
            day_index=day.day_index,
            base_city_id=day.base_city_id,
            base_city_name=day.base_city.name if day.base_city else None,
            notes=day.notes,
            stops=[],  # New day has no stops yet
            created_at=day.created_at.isoformat(),
            updated_at=day.updated_at.isoformat(),
        )
    
    async def update_trip_day(
        self,
        user_id: int,
        trip_id: int,
        day_id: int,
        request: UpdateTripDayRequest,
    ) -> TripDayResponse:
        """
        Update a trip day.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            day_id: ID of the day to update
            request: UpdateTripDayRequest with fields to update
            
        Returns:
            TripDayResponse for the updated day
            
        Raises:
            ValueError: If trip/day not found, doesn't belong to user, or city not found
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Get the day and verify it belongs to the trip
        day = await TripDay.filter(id=day_id, trip_id=trip_id).first()
        if not day:
            raise ValueError(f"Day {day_id} not found or doesn't belong to trip {trip_id}")
        
        # Verify base_city_id if provided
        if request.base_city_id is not None:
            if request.base_city_id:
                city = await City.filter(id=request.base_city_id).first()
                if not city:
                    raise ValueError(f"City {request.base_city_id} not found")
            day.base_city_id = request.base_city_id
        
        # Update notes if provided
        if request.notes is not None:
            day.notes = request.notes
        
        await day.save()
        await day.fetch_related('base_city', 'stops__attraction')
        
        # Get stops for this day
        from core.models.trips.trip_stop import TripStop
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
        
        # Return response
        return TripDayResponse(
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
    
    async def delete_trip_day(
        self,
        user_id: int,
        trip_id: int,
        day_id: int,
    ) -> None:
        """
        Delete a trip day (and all its stops via CASCADE).
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            day_id: ID of the day to delete
            
        Raises:
            ValueError: If trip/day not found or doesn't belong to user
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Get the day and verify it belongs to the trip
        day = await TripDay.filter(id=day_id, trip_id=trip_id).first()
        if not day:
            raise ValueError(f"Day {day_id} not found or doesn't belong to trip {trip_id}")
        
        # Delete the day (stops will be deleted via CASCADE)
        await day.delete()

