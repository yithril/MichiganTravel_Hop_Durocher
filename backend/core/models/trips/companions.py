"""Companions enumeration."""
from enum import Enum


class Companions(str, Enum):
    """Companions enumeration."""
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    FRIENDS = "friends"

