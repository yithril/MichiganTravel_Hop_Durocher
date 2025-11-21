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


class AttractionResponse(BaseModel):
    """Response DTO for an attraction."""
    id: int
    name: str
    type: str
    description: Optional[str] = None
    city_id: int
    city_name: str
    latitude: float
    longitude: float
    url: Optional[str] = None
    price_level: Optional[str] = None
    hidden_gem_score: Optional[float] = None
    seasonality: Optional[str] = None
    vibes: List[AttractionVibeInfo]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AttractionsListResponse(BaseModel):
    """Response DTO for listing attractions."""
    attractions: List[AttractionResponse]
    total: int
    trip_id: Optional[int] = None  # If filtered by trip
    matching_vibe_ids: Optional[List[int]] = None  # Vibes used for filtering

