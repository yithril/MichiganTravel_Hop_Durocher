"""Trip stop slot enumeration."""
from enum import Enum


class TripStopSlot(str, Enum):
    """Trip stop slot enumeration."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    FLEX = "flex"

