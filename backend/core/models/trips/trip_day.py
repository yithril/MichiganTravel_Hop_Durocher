"""TripDay model for individual days in a trip."""
from tortoise import fields
from core.models.base import BaseModel


class TripDay(BaseModel):
    """TripDay model representing one day of a trip."""
    
    trip = fields.ForeignKeyField(
        "models.Trip",
        related_name="days",
        on_delete=fields.CASCADE
    )
    day_index = fields.IntField()  # 1-based: 1, 2, 3, ...
    base_city = fields.ForeignKeyField(
        "models.City",
        related_name="trip_days",
        null=True,
        on_delete=fields.SET_NULL
    )
    notes = fields.TextField(null=True)
    
    class Meta:
        table = "trip_days"
    
    def __str__(self):
        return f"TripDay(id={self.id}, trip_id={self.trip_id}, day_index={self.day_index})"

