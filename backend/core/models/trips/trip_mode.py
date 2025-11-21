"""Trip mode enumeration."""
from enum import Enum


class TripMode(str, Enum):
    """Trip mode enumeration."""
    LOCAL_HUB = "local_hub"
    ROAD_TRIP = "road_trip"

