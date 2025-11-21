"""City model for trip destinations."""
from tortoise import fields
from core.models.base import BaseModel


class City(BaseModel):
    """City model representing a town/hub for trips."""
    
    name = fields.CharField(max_length=255)
    state = fields.CharField(max_length=2, default="MI")
    region = fields.CharField(max_length=100, null=True)  # e.g., "West Michigan", "UP"
    latitude = fields.DecimalField(max_digits=10, decimal_places=8)
    longitude = fields.DecimalField(max_digits=10, decimal_places=8)
    slug = fields.CharField(max_length=255, unique=True)  # For URLs
    hidden_gem_score = fields.DecimalField(max_digits=4, decimal_places=2, null=True)  # 0-10
    
    class Meta:
        table = "cities"
    
    def __str__(self):
        return f"City(name={self.name}, state={self.state})"

