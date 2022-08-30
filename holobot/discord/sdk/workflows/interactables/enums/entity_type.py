from enum import IntEnum, unique

@unique
class EntityType(IntEnum):
    """Defines the valid values for entity types."""

    SERVER = 0
    """Marks a server."""

    CHANNEL = 1
    """Marks either a standalone channel (eg. DM) or a server-owned channel."""

    USER = 2
    """Marks either a standalone user or a server member."""
