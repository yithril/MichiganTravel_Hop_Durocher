"""Data Transfer Objects for trip seed operations."""
from typing import Optional, List
from pydantic import BaseModel


class TripSeedMessageRequest(BaseModel):
    """Request DTO for sending a message to the trip seed agent."""
    message: str
    conversation_id: Optional[int] = None  # If None, creates new conversation


class TripSeedStateResponse(BaseModel):
    """Response DTO for TripSeed state information."""
    trip_seed_id: int
    conversation_id: int
    num_days: Optional[int] = None
    trip_mode: Optional[str] = None
    budget_band: Optional[str] = None
    start_location_text: Optional[str] = None
    companions: Optional[str] = None
    status: str
    is_complete: bool
    missing_fields: List[str]


class TripSeedAgentResponse(BaseModel):
    """Response DTO from trip seed agent endpoint."""
    response_text: str
    conversation_id: int
    trip_seed_state: TripSeedStateResponse
    is_complete: bool

