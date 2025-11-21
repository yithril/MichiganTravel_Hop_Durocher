"""CityVibe join table for many-to-many relationship."""
from tortoise import fields
from tortoise.models import Model


class CityVibe(Model):
    """Join table associating City with Vibes."""
    
    city = fields.ForeignKeyField(
        "models.City",
        related_name="city_vibes",
        on_delete=fields.CASCADE
    )
    vibe = fields.ForeignKeyField(
        "models.Vibe",
        related_name="city_vibes",
        on_delete=fields.CASCADE
    )
    strength = fields.DecimalField(max_digits=3, decimal_places=2)  # 0-1
    
    class Meta:
        table = "city_vibes"
        unique_together = [("city", "vibe")]
    
    def __str__(self):
        return f"CityVibe(city_id={self.city_id}, vibe_id={self.vibe_id}, strength={self.strength})"

