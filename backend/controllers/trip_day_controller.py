"""Trip day controller for managing trip days."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from core.dependencies import CurrentUser
from dtos.trip_day_dto import (
    TripDayResponse,
    CreateTripDayRequest,
    UpdateTripDayRequest,
)
from services.trip_day_service import TripDayService

router = APIRouter(prefix="/api/trips/{trip_id}/days", tags=["trip-days"])


def get_trip_day_service() -> TripDayService:
    """
    Dependency to get TripDayService instance.
    """
    return TripDayService()


@router.get("", response_model=List[TripDayResponse])
async def get_trip_days(
    trip_id: int,
    user: CurrentUser,
    trip_day_service: TripDayService = Depends(get_trip_day_service),
) -> List[TripDayResponse]:
    """
    Get all days for a trip.
    
    Args:
        trip_id: ID of the trip
        user: Current authenticated user (from dependency)
        trip_day_service: Trip day service (from dependency)
        
    Returns:
        List of TripDayResponse objects
        
    Raises:
        HTTPException 400: If trip not found or doesn't belong to user
    """
    try:
        return await trip_day_service.get_trip_days(
            user_id=user.id,
            trip_id=trip_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("", response_model=TripDayResponse, status_code=status.HTTP_201_CREATED)
async def create_trip_day(
    trip_id: int,
    request: CreateTripDayRequest,
    user: CurrentUser,
    trip_day_service: TripDayService = Depends(get_trip_day_service),
) -> TripDayResponse:
    """
    Create a new day for a trip.
    
    Args:
        trip_id: ID of the trip
        request: CreateTripDayRequest with day_index, base_city_id, and notes
        user: Current authenticated user (from dependency)
        trip_day_service: Trip day service (from dependency)
        
    Returns:
        TripDayResponse for the newly created day
        
    Raises:
        HTTPException 400: If trip not found, doesn't belong to user, or day_index already exists
    """
    try:
        return await trip_day_service.create_trip_day(
            user_id=user.id,
            trip_id=trip_id,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{day_id}", response_model=TripDayResponse)
async def update_trip_day(
    trip_id: int,
    day_id: int,
    request: UpdateTripDayRequest,
    user: CurrentUser,
    trip_day_service: TripDayService = Depends(get_trip_day_service),
) -> TripDayResponse:
    """
    Update a trip day.
    
    Args:
        trip_id: ID of the trip
        day_id: ID of the day to update
        request: UpdateTripDayRequest with fields to update
        user: Current authenticated user (from dependency)
        trip_day_service: Trip day service (from dependency)
        
    Returns:
        TripDayResponse for the updated day
        
    Raises:
        HTTPException 400: If trip/day not found, doesn't belong to user, or city not found
    """
    try:
        return await trip_day_service.update_trip_day(
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


@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip_day(
    trip_id: int,
    day_id: int,
    user: CurrentUser,
    trip_day_service: TripDayService = Depends(get_trip_day_service),
) -> None:
    """
    Delete a trip day (and all its stops via CASCADE).
    
    Args:
        trip_id: ID of the trip
        day_id: ID of the day to delete
        user: Current authenticated user (from dependency)
        trip_day_service: Trip day service (from dependency)
        
    Raises:
        HTTPException 400: If trip/day not found or doesn't belong to user
    """
    try:
        await trip_day_service.delete_trip_day(
            user_id=user.id,
            trip_id=trip_id,
            day_id=day_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

