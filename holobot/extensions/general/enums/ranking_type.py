from enum import IntEnum, unique

@unique
class RankingType(IntEnum):
    """Defines the valid values for marriage ranking types."""

    LEVEL = 0
    """The ranking that is ordered by marriage level."""

    AGE = 1
    """The ranking that is ordered by marriage age."""
