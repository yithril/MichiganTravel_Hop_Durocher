"""Budget band enumeration."""
from enum import Enum


class BudgetBand(str, Enum):
    """Budget band enumeration."""
    RELAXED = "relaxed"
    COMFORTABLE = "comfortable"
    SPLURGE = "splurge"

