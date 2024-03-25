from enum import IntEnum, unique

@unique
class QuestStatus(IntEnum):
    """Defines the quest statuses."""

    MISSING = 0
    """The quest doesn't exist."""

    UNAVAILABLE = 1
    """The quest is currently unavailable."""

    AVAILABLE = 2
    """The quest is available for the user."""

    IN_PROGRESS = 3
    """The quest is currently in progress by the user."""
