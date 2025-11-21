"""TripVibe join table for many-to-many relationship."""
from tortoise import fields
from tortoise.models import Model


class TripVibe(Model):
    """Join table associating Trip with Vibes."""
    
    trip = fields.ForeignKeyField(
        "models.Trip",
        related_name="trip_vibes",
        on_delete=fields.CASCADE
    )
    vibe = fields.ForeignKeyField(
        "models.Vibe",
        related_name="trip_vibes",
        on_delete=fields.CASCADE
    )
    strength = fields.DecimalField(max_digits=3, decimal_places=2)  # 0-1
    
    class Meta:
        table = "trip_vibes"
        unique_together = [("trip", "vibe")]
    
    def __str__(self):
        return f"TripVibe(trip_id={self.trip_id}, vibe_id={self.vibe_id}, strength={self.strength})"

