"""Data Transfer Objects for attraction operations."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    pass  # Forward references handled via string annotations


class AttractionVibeInfo(BaseModel):
    """Vibe information for an attraction."""
    vibe_id: int
    vibe_code: str
    vibe_label: str
    strength: float  # 0-1
    
    class Config:
        from_attributes = True


class AttractionsListResponse(BaseModel):
    """Response DTO for listing attractions."""
    attractions: List[AttractionResponse]
    total: int
    trip_id: Optional[int] = None  # If filtered by trip
    matching_vibe_ids: Optional[List[int]] = None  # Vibes used for filtering

