"""Data Transfer Objects for trip stop operations."""
from typing import Optional, List
from pydantic import BaseModel


class TripStopResponse(BaseModel):
    """Response DTO for a trip stop."""
    id: int
    trip_day_id: int
    attraction_id: Optional[int] = None
    attraction_name: Optional[str] = None
    attraction_type: Optional[str] = None
    label: Optional[str] = None
    slot: str  # morning, afternoon, evening, flex
    order_index: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class CreateTripStopRequest(BaseModel):
    """Request DTO for creating a trip stop."""
    attraction_id: Optional[int] = None
    label: Optional[str] = None
    slot: str  # morning, afternoon, evening, flex
    order_index: int


class UpdateTripStopRequest(BaseModel):
    """Request DTO for updating a trip stop."""
    attraction_id: Optional[int] = None
    label: Optional[str] = None
    slot: Optional[str] = None  # morning, afternoon, evening, flex
    order_index: Optional[int] = None


class StopOrderItem(BaseModel):
    """Item in reorder request."""
    stop_id: int
    order_index: int


class ReorderStopsRequest(BaseModel):
    """Request DTO for reordering stops within a day."""
    stop_orders: List[StopOrderItem]

