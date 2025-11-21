"""TripSeedVibe join table for many-to-many relationship."""
from tortoise import fields
from tortoise.models import Model


class TripSeedVibe(Model):
    """Join table associating TripSeed with Vibes."""
    
    trip_seed = fields.ForeignKeyField(
        "models.TripSeed",
        related_name="trip_seed_vibes",
        on_delete=fields.CASCADE
    )
    vibe = fields.ForeignKeyField(
        "models.Vibe",
        related_name="trip_seed_vibes",
        on_delete=fields.CASCADE
    )
    strength = fields.DecimalField(max_digits=3, decimal_places=2)  # 0-1
    
    class Meta:
        table = "trip_seed_vibes"
        unique_together = [("trip_seed", "vibe")]
    
    def __str__(self):
        return f"TripSeedVibe(trip_seed_id={self.trip_seed_id}, vibe_id={self.vibe_id}, strength={self.strength})"

