"""Data Transfer Objects for trip operations."""
from typing import Optional, List
from pydantic import BaseModel


class TripResponse(BaseModel):
    """Response DTO for a trip."""
    id: int
    name: str
    user_id: int
    start_location_text: Optional[str] = None
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    num_days: int
    trip_mode: str
    budget_band: str
    companions: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ActiveTripSeedResponse(BaseModel):
    """Response DTO for an active trip seed (in progress conversation)."""
    trip_seed_id: int
    conversation_id: int
    status: str  # DRAFT or COMPLETE
    num_days: Optional[int] = None
    trip_mode: Optional[str] = None
    budget_band: Optional[str] = None
    start_location_text: Optional[str] = None
    companions: Optional[str] = None
    is_complete: bool
    missing_fields: List[str]
    updated_at: str  # Last activity timestamp
    
    class Config:
        from_attributes = True


class TripsListResponse(BaseModel):
    """Response DTO for listing trips and active trip seeds."""
    trips: List[TripResponse]  # Completed/saved trips
    active_trip_seeds: List[ActiveTripSeedResponse]  # In-progress conversations
    total_trips: int
    total_active: int

