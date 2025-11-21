"""TripStop model for activities within a trip day."""
from tortoise import fields
from core.models.base import BaseModel
from core.models.trips.trip_stop_slot import TripStopSlot


class TripStop(BaseModel):
    """TripStop model representing an activity/stop within a day."""
    
    trip_day = fields.ForeignKeyField(
        "models.TripDay",
        related_name="stops",
        on_delete=fields.CASCADE
    )
    attraction = fields.ForeignKeyField(
        "models.Attraction",
        related_name="trip_stops",
        null=True,
        on_delete=fields.SET_NULL
    )
    label = fields.CharField(max_length=255, null=True)  # For free-text items
    slot = fields.CharEnumField(TripStopSlot)
    order_index = fields.IntField()  # For ordering stops within a day
    
    class Meta:
        table = "trip_stops"
    
    def __str__(self):
        return f"TripStop(id={self.id}, trip_day_id={self.trip_day_id}, slot={self.slot}, order_index={self.order_index})"

