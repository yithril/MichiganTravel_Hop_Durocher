"""Attraction model for places to visit."""
from tortoise import fields
from core.models.base import BaseModel


class Attraction(BaseModel):
    """Attraction model for things to do (cafés, trails, cider mills, etc.)."""
    
    city = fields.ForeignKeyField(
        "models.City",
        related_name="attractions",
        on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=255)
    type = fields.CharField(max_length=100)  # e.g., "cafe", "trail", "cider_mill"
    description = fields.TextField(null=True)
    latitude = fields.DecimalField(max_digits=10, decimal_places=8)
    longitude = fields.DecimalField(max_digits=10, decimal_places=8)
    url = fields.CharField(max_length=512, null=True)  # Real website if exists
    mini_site_slug = fields.CharField(max_length=255, unique=True, null=True)  # For generated pages
    price_level = fields.CharField(max_length=10, null=True)  # "$", "$$", "$$$"
    hidden_gem_score = fields.DecimalField(max_digits=4, decimal_places=2, null=True)  # 0-10
    ai_discovered = fields.BooleanField(default=False)
    confidence = fields.DecimalField(max_digits=3, decimal_places=2, null=True)  # 0-1
    seasonality = fields.CharField(max_length=50, null=True)  # e.g., "all_year", "summer", "fall"
    image_url = fields.CharField(max_length=500, null=True)  # URL to attraction image
    
    class Meta:
        table = "attractions"
    
    def __str__(self):
        return f"Attraction(name={self.name}, type={self.type}, city_id={self.city_id})"

