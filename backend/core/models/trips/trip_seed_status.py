"""Trip seed status enumeration."""
from enum import Enum


class TripSeedStatus(str, Enum):
    """Trip seed status enumeration."""
    DRAFT = "draft"
    COMPLETE = "complete"
    FINALIZED = "finalized"

