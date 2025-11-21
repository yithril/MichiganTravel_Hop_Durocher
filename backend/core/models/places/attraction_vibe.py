"""AttractionVibe join table for many-to-many relationship."""
from tortoise import fields
from tortoise.models import Model


class AttractionVibe(Model):
    """Join table associating Attraction with Vibes."""
    
    attraction = fields.ForeignKeyField(
        "models.Attraction",
        related_name="attraction_vibes",
        on_delete=fields.CASCADE
    )
    vibe = fields.ForeignKeyField(
        "models.Vibe",
        related_name="attraction_vibes",
        on_delete=fields.CASCADE
    )
    strength = fields.DecimalField(max_digits=3, decimal_places=2)  # 0-1
    
    class Meta:
        table = "attraction_vibes"
        unique_together = [("attraction", "vibe")]
    
    def __str__(self):
        return f"AttractionVibe(attraction_id={self.attraction_id}, vibe_id={self.vibe_id}, strength={self.strength})"

