from enum import IntEnum, unique

@unique
class OptionType(IntEnum):
    """Defines the valid values for option types."""

    STRING = 0
    BOOLEAN = 1
    INTEGER = 2
    FLOAT = 3
