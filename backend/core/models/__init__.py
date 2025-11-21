"""Models package."""
from core.models.base import BaseModel
from core.models.user import User
from core.models.image import Image
from core.models.conversation import Conversation, Message

# Places domain
from core.models.places import (
    Vibe,
    City,
    Attraction,
    CityVibe,
    AttractionVibe,
)

# Trips domain
from core.models.trips import (
    TripMode,
    BudgetBand,
    Companions,
    TripStopSlot,
    TripSeedStatus,
    TripSeed,
    TripSeedVibe,
    Trip,
    TripVibe,
    TripDay,
    TripStop,
)

__all__ = [
    # Base
    "BaseModel",
    # User & Auth
    "User",
    # Storage
    "Image",
    # Conversations
    "Conversation",
    "Message",
    # Places domain
    "Vibe",
    "City",
    "Attraction",
    "CityVibe",
    "AttractionVibe",
    # Trips domain - Enums
    "TripMode",
    "BudgetBand",
    "Companions",
    "TripStopSlot",
    "TripSeedStatus",
    # Trips domain - Models
    "TripSeed",
    "TripSeedVibe",
    "Trip",
    "TripVibe",
    "TripDay",
    "TripStop",
]

