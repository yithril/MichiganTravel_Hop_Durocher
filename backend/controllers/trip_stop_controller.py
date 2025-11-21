"""Trip stop controller for managing trip stops (activities)."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from core.dependencies import CurrentUser
from dtos.trip_stop_dto import (
    TripStopResponse,
    CreateTripStopRequest,
    UpdateTripStopRequest,
    ReorderStopsRequest,
)
from services.trip_stop_service import TripStopService

router = APIRouter(prefix="/api/trips/{trip_id}/days/{day_id}/stops", tags=["trip-stops"])


def get_trip_stop_service() -> TripStopService:
    """
    Dependency to get TripStopService instance.
    """
    return TripStopService()


@router.get("", response_model=List[TripStopResponse])
async def get_trip_stops(
    trip_id: int,
    day_id: int,
    user: CurrentUser,
    trip_stop_service: TripStopService = Depends(get_trip_stop_service),
) -> List[TripStopResponse]:
    """
    Get all stops for a trip day.
    
    Args:
        trip_id: ID of the trip
        day_id: ID of the day
        user: Current authenticated user (from dependency)
        trip_stop_service: Trip stop service (from dependency)
        
    Returns:
        List of TripStopResponse objects
        
    Raises:
        HTTPException 400: If trip/day not found or doesn't belong to user
    """
    try:
        return await trip_stop_service.get_trip_stops(
            user_id=user.id,
            trip_id=trip_id,
            day_id=day_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("", response_model=TripStopResponse, status_code=status.HTTP_201_CREATED)
async def create_trip_stop(
    trip_id: int,
    day_id: int,
    request: CreateTripStopRequest,
    user: CurrentUser,
    trip_stop_service: TripStopService = Depends(get_trip_stop_service),
) -> TripStopResponse:
    """
    Create a new stop (activity) for a trip day.
    
    Args:
        trip_id: ID of the trip
        day_id: ID of the day
        request: CreateTripStopRequest with stop details
        user: Current authenticated user (from dependency)
        trip_stop_service: Trip stop service (from dependency)
        
    Returns:
        TripStopResponse for the newly created stop
        
    Raises:
        HTTPException 400: If trip/day not found, doesn't belong to user, or validation fails
    """
    try:
        return await trip_stop_service.create_trip_stop(
            user_id=user.id,
            trip_id=trip_id,
            day_id=day_id,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{stop_id}", response_model=TripStopResponse)
async def update_trip_stop(
    trip_id: int,
    day_id: int,
    stop_id: int,
    request: UpdateTripStopRequest,
    user: CurrentUser,
    trip_stop_service: TripStopService = Depends(get_trip_stop_service),
) -> TripStopResponse:
    """
    Update a trip stop.
    
    Args:
        trip_id: ID of the trip
        day_id: ID of the day
        stop_id: ID of the stop to update
        request: UpdateTripStopRequest with fields to update
        user: Current authenticated user (from dependency)
        trip_stop_service: Trip stop service (from dependency)
        
    Returns:
        TripStopResponse for the updated stop
        
    Raises:
        HTTPException 400: If trip/day/stop not found, doesn't belong to user, or validation fails
    """
    try:
        return await trip_stop_service.update_trip_stop(
            user_id=user.id,
            trip_id=trip_id,
            day_id=day_id,
            stop_id=stop_id,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip_stop(
    trip_id: int,
    day_id: int,
    stop_id: int,
    user: CurrentUser,
    trip_stop_service: TripStopService = Depends(get_trip_stop_service),
) -> None:
    """
    Delete a trip stop.
    
    Args:
        trip_id: ID of the trip
        day_id: ID of the day
        stop_id: ID of the stop to delete
        user: Current authenticated user (from dependency)
        trip_stop_service: Trip stop service (from dependency)
        
    Raises:
        HTTPException 400: If trip/day/stop not found or doesn't belong to user
    """
    try:
        await trip_stop_service.delete_trip_stop(
            user_id=user.id,
            trip_id=trip_id,
            day_id=day_id,
            stop_id=stop_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/reorder", response_model=List[TripStopResponse])
async def reorder_stops(
    trip_id: int,
    day_id: int,
    request: ReorderStopsRequest,
    user: CurrentUser,
    trip_stop_service: TripStopService = Depends(get_trip_stop_service),
) -> List[TripStopResponse]:
    """
    Reorder stops within a day.
    
    Args:
        trip_id: ID of the trip
        day_id: ID of the day
        request: ReorderStopsRequest with list of {stop_id, order_index} mappings
        user: Current authenticated user (from dependency)
        trip_stop_service: Trip stop service (from dependency)
        
    Returns:
        List of TripStopResponse objects in new order
        
    Raises:
        HTTPException 400: If trip/day not found, doesn't belong to user, or validation fails
    """
    try:
        return await trip_stop_service.reorder_stops(
            user_id=user.id,
            trip_id=trip_id,
            day_id=day_id,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

