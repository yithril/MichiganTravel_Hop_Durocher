"""Data Transfer Objects for trip day operations."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from dtos.trip_stop_dto import TripStopResponse


class TripDayResponse(BaseModel):
    """Response DTO for a trip day."""
    id: int
    trip_id: int
    day_index: int
    base_city_id: Optional[int] = None
    base_city_name: Optional[str] = None
    notes: Optional[str] = None
    stops: List["TripStopResponse"]  # Nested stops (forward reference)
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class CreateTripDayRequest(BaseModel):
    """Request DTO for creating a trip day."""
    day_index: int
    base_city_id: Optional[int] = None
    notes: Optional[str] = None


class UpdateTripDayRequest(BaseModel):
    """Request DTO for updating a trip day."""
    base_city_id: Optional[int] = None
    notes: Optional[str] = None


# Resolve forward references at module level
# This allows TripDayResponse to reference TripStopResponse
def _resolve_forward_refs():
    """Resolve forward references after TripStopResponse is available."""
    try:
        from dtos.trip_stop_dto import TripStopResponse
        TripDayResponse.model_rebuild()
    except (ImportError, AttributeError):
        # Will be resolved when trip_stop_dto is imported, or if using Pydantic v1
        pass

_resolve_forward_refs()

