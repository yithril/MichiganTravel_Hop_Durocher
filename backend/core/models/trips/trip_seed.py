"""TripSeed model for storing trip planning session data."""
from tortoise import fields
from core.models.base import BaseModel
from core.models.trips.trip_mode import TripMode
from core.models.trips.budget_band import BudgetBand
from core.models.trips.companions import Companions
from core.models.trips.trip_seed_status import TripSeedStatus


class TripSeed(BaseModel):
    """TripSeed model for storing trip planning data from AI conversations."""
    
    conversation = fields.ForeignKeyField(
        "models.Conversation",
        related_name="trip_seeds",
        on_delete=fields.CASCADE
    )
    trip = fields.ForeignKeyField(
        "models.Trip",
        related_name="trip_seed",
        null=True,
        on_delete=fields.SET_NULL
    )
    start_location_text = fields.CharField(max_length=255, null=True)
    start_latitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    start_longitude = fields.DecimalField(max_digits=10, decimal_places=8, null=True)
    num_days = fields.IntField()
    trip_mode = fields.CharEnumField(TripMode)
    budget_band = fields.CharEnumField(BudgetBand)
    companions = fields.CharEnumField(Companions, null=True)
    status = fields.CharEnumField(TripSeedStatus, default=TripSeedStatus.DRAFT)
    
    class Meta:
        table = "trip_seeds"
    
    def __str__(self):
        return f"TripSeed(id={self.id}, conversation_id={self.conversation_id}, status={self.status})"

