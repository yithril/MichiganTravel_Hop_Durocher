"""Attraction controller for querying attractions by vibes."""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from core.dependencies import CurrentUser
from core.models.user import User
from dtos.attraction_dto import AttractionsListResponse
from services.attraction_service import AttractionService

router = APIRouter(prefix="/api/attractions", tags=["attractions"])


def get_attraction_service() -> AttractionService:
    """
    Dependency to get AttractionService instance.
    """
    return AttractionService()


@router.get("", response_model=AttractionsListResponse)
async def get_attractions(
    user: CurrentUser,
    trip_id: Optional[int] = Query(None, description="Filter attractions by trip vibes"),
    vibe_ids: Optional[str] = Query(None, description="Comma-separated list of vibe IDs"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    attraction_service: AttractionService = Depends(get_attraction_service),
) -> AttractionsListResponse:
    """
    Get attractions filtered by vibes.
    
    Either trip_id or vibe_ids must be provided.
    - If trip_id is provided, uses vibes from that trip
    - If vibe_ids is provided, uses those specific vibes
    
    Args:
        user: Current authenticated user (from dependency)
        trip_id: Optional trip ID to get vibes from
        vibe_ids: Optional comma-separated list of vibe IDs
        limit: Optional limit on number of results
        attraction_service: Attraction service (from dependency)
        
    Returns:
        AttractionsListResponse with matching attractions
        
    Raises:
        400: If neither trip_id nor vibe_ids is provided
    """
    if trip_id:
        # Get attractions matching trip vibes
        return await attraction_service.get_attractions_by_trip_vibes(
            user_id=user.id,
            trip_id=trip_id,
            limit=limit,
        )
    elif vibe_ids:
        # Parse comma-separated vibe IDs
        try:
            vibe_id_list = [int(vid.strip()) for vid in vibe_ids.split(",") if vid.strip()]
        except ValueError:
            raise ValueError("vibe_ids must be comma-separated integers")
        
        return await attraction_service.get_attractions_by_vibes(
            vibe_ids=vibe_id_list,
            limit=limit,
        )
    else:
        raise ValueError("Either trip_id or vibe_ids must be provided")

