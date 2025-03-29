from enum import IntEnum, unique

@unique
class GrantItemOutcome(IntEnum):
    GRANTED = 0
    """Marks that the item has been granted to the user."""

    GRANTED_ALREADY = 1
    """
    Marks that the item had been granted to the user previously;
    therefore, this time it hasn't been granted again.
    """
