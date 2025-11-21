"""
Service for managing trip stops.

This service handles CRUD operations for TripStops.
"""
from typing import List
from core.models.trips.trip import Trip
from core.models.trips.trip_day import TripDay
from core.models.trips.trip_stop import TripStop
from core.models.trips.trip_stop_slot import TripStopSlot
from core.models.places.attraction import Attraction
from dtos.trip_stop_dto import (
    TripStopResponse,
    CreateTripStopRequest,
    UpdateTripStopRequest,
    ReorderStopsRequest,
)


class TripStopService:
    """Service for managing trip stops."""
    
    async def get_trip_stops(
        self,
        user_id: int,
        trip_id: int,
        day_id: int,
    ) -> List[TripStopResponse]:
        """
        Get all stops for a trip day.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            day_id: ID of the day
            
        Returns:
            List of TripStopResponse objects
            
        Raises:
            ValueError: If trip/day not found or doesn't belong to user
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Verify day belongs to trip
        day = await TripDay.filter(id=day_id, trip_id=trip_id).first()
        if not day:
            raise ValueError(f"Day {day_id} not found or doesn't belong to trip {trip_id}")
        
        # Get all stops for this day
        stops = await TripStop.filter(trip_day_id=day_id).prefetch_related(
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
        
        return stop_responses
    
    async def create_trip_stop(
        self,
        user_id: int,
        trip_id: int,
        day_id: int,
        request: CreateTripStopRequest,
    ) -> TripStopResponse:
        """
        Create a new stop for a trip day.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            day_id: ID of the day
            request: CreateTripStopRequest with stop details
            
        Returns:
            TripStopResponse for the newly created stop
            
        Raises:
            ValueError: If trip/day not found, doesn't belong to user, or validation fails
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Verify day belongs to trip
        day = await TripDay.filter(id=day_id, trip_id=trip_id).first()
        if not day:
            raise ValueError(f"Day {day_id} not found or doesn't belong to trip {trip_id}")
        
        # Validate that either attraction_id or label is provided
        if not request.attraction_id and not request.label:
            raise ValueError("Either attraction_id or label must be provided")
        
        # Verify attraction_id if provided
        if request.attraction_id:
            attraction = await Attraction.filter(id=request.attraction_id).first()
            if not attraction:
                raise ValueError(f"Attraction {request.attraction_id} not found")
        
        # Validate slot
        try:
            slot = TripStopSlot(request.slot)
        except ValueError:
            raise ValueError(f"Invalid slot: {request.slot}. Must be one of: morning, afternoon, evening, flex")
        
        # Check for duplicate attraction in the same day
        if request.attraction_id:
            existing_stop = await TripStop.filter(
                trip_day_id=day_id,
                attraction_id=request.attraction_id
            ).first()
            if existing_stop:
                raise ValueError(f"This activity is already added to this day")
        
        # Create the stop
        stop = await TripStop.create(
            trip_day_id=day_id,
            attraction_id=request.attraction_id,
            label=request.label,
            slot=slot,
            order_index=request.order_index,
        )
        
        # Reload with relations
        await stop.fetch_related('attraction')
        
        # Return response
        return TripStopResponse(
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
    
    async def update_trip_stop(
        self,
        user_id: int,
        trip_id: int,
        day_id: int,
        stop_id: int,
        request: UpdateTripStopRequest,
    ) -> TripStopResponse:
        """
        Update a trip stop.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            day_id: ID of the day
            stop_id: ID of the stop to update
            request: UpdateTripStopRequest with fields to update
            
        Returns:
            TripStopResponse for the updated stop
            
        Raises:
            ValueError: If trip/day/stop not found, doesn't belong to user, or validation fails
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Verify day belongs to trip
        day = await TripDay.filter(id=day_id, trip_id=trip_id).first()
        if not day:
            raise ValueError(f"Day {day_id} not found or doesn't belong to trip {trip_id}")
        
        # Get the stop and verify it belongs to the day
        stop = await TripStop.filter(id=stop_id, trip_day_id=day_id).first()
        if not stop:
            raise ValueError(f"Stop {stop_id} not found or doesn't belong to day {day_id}")
        
        # Update attraction_id if provided
        if request.attraction_id is not None:
            if request.attraction_id:
                attraction = await Attraction.filter(id=request.attraction_id).first()
                if not attraction:
                    raise ValueError(f"Attraction {request.attraction_id} not found")
            stop.attraction_id = request.attraction_id
        
        # Update label if provided
        if request.label is not None:
            stop.label = request.label
        
        # Update slot if provided
        if request.slot is not None:
            try:
                slot = TripStopSlot(request.slot)
            except ValueError:
                raise ValueError(f"Invalid slot: {request.slot}. Must be one of: morning, afternoon, evening, flex")
            stop.slot = slot
        
        # Update order_index if provided
        if request.order_index is not None:
            stop.order_index = request.order_index
        
        # Validate that either attraction_id or label is set after update
        if not stop.attraction_id and not stop.label:
            raise ValueError("Either attraction_id or label must be provided")
        
        await stop.save()
        await stop.fetch_related('attraction')
        
        # Return response
        return TripStopResponse(
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
    
    async def delete_trip_stop(
        self,
        user_id: int,
        trip_id: int,
        day_id: int,
        stop_id: int,
    ) -> None:
        """
        Delete a trip stop.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            day_id: ID of the day
            stop_id: ID of the stop to delete
            
        Raises:
            ValueError: If trip/day/stop not found or doesn't belong to user
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Verify day belongs to trip
        day = await TripDay.filter(id=day_id, trip_id=trip_id).first()
        if not day:
            raise ValueError(f"Day {day_id} not found or doesn't belong to trip {trip_id}")
        
        # Get the stop and verify it belongs to the day
        stop = await TripStop.filter(id=stop_id, trip_day_id=day_id).first()
        if not stop:
            raise ValueError(f"Stop {stop_id} not found or doesn't belong to day {day_id}")
        
        # Delete the stop
        await stop.delete()
    
    async def reorder_stops(
        self,
        user_id: int,
        trip_id: int,
        day_id: int,
        request: ReorderStopsRequest,
    ) -> List[TripStopResponse]:
        """
        Reorder stops within a day.
        
        Args:
            user_id: ID of the user
            trip_id: ID of the trip
            day_id: ID of the day
            request: ReorderStopsRequest with list of {stop_id, order_index} mappings
            
        Returns:
            List of TripStopResponse objects in new order
            
        Raises:
            ValueError: If trip/day not found, doesn't belong to user, or validation fails
        """
        # Verify trip belongs to user
        trip = await Trip.filter(id=trip_id, user_id=user_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found or doesn't belong to user")
        
        # Verify day belongs to trip
        day = await TripDay.filter(id=day_id, trip_id=trip_id).first()
        if not day:
            raise ValueError(f"Day {day_id} not found or doesn't belong to trip {trip_id}")
        
        # Validate that all stop_ids belong to this day
        stop_ids = [item.stop_id for item in request.stop_orders]
        existing_stops = await TripStop.filter(
            id__in=stop_ids,
            trip_day_id=day_id
        ).all()
        
        if len(existing_stops) != len(stop_ids):
            raise ValueError("One or more stop IDs do not belong to this day")
        
        # Update order_index for each stop
        stop_map = {item.stop_id: item.order_index for item in request.stop_orders}
        for stop in existing_stops:
            if stop.id in stop_map:
                stop.order_index = stop_map[stop.id]
                await stop.save()
        
        # Reload all stops with relations and return in new order
        stops = await TripStop.filter(trip_day_id=day_id).prefetch_related(
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
        
        return stop_responses

