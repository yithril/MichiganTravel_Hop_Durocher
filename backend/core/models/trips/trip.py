"""Trip model for saved trip itineraries."""
from tortoise import fields
from core.models.base import BaseModel
from core.models.trips.trip_mode import TripMode
from core.models.trips.budget_band import BudgetBand
from core.models.trips.companions import Companions
from core.models.trips.trip_status import TripStatus


class Trip(BaseModel):
    """Trip model representing a completed/saved trip itinerary."""
    
    user = fields.ForeignKeyField(
        "models.User",
        related_name="trips",
        on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=255)  # Required
    start_location_text = fields.CharField(max_length=255, null=True)
    start_latitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    start_longitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    num_days = fields.IntField()
    trip_mode = fields.CharEnumField(TripMode)
    budget_band = fields.CharEnumField(BudgetBand)
    companions = fields.CharEnumField(Companions, null=True)
    status = fields.CharEnumField(TripStatus, default=TripStatus.PLANNED)
    
    class Meta:
        table = "trips"
    
    def __str__(self):
        return f"Trip(id={self.id}, name={self.name}, user_id={self.user_id}, status={self.status})"

