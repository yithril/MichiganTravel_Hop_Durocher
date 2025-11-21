"""Trip status enumeration."""
from enum import Enum


class TripStatus(str, Enum):
    """Trip status enumeration."""
    PLANNED = "planned"  # Trip is planned but user hasn't gone on it yet
    COMPLETED = "completed"  # User has gone on the trip (can upload photos, etc. in future)

