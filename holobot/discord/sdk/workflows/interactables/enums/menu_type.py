from enum import IntEnum, unique

@unique
class MenuType(IntEnum):
    """Defines the valid values for menu item types."""

    USER = 0
    MESSAGE = 1
