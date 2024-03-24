from enum import IntEnum, unique

@unique
class QuestResetType(IntEnum):
    """Defines the type of quest resets.

    This is tied to each player's own completion,
    unless a script changes this behavior ("CUSTOM").
    """

    NONE = 0
    """The quest never resets, it can only be done once."""

    INTERVAL = 1
    """The quest resets after a specific amount of time passes
    since its completion.
    """

    DAILY_AT = 2
    """The quest resets every day at a specific offset."""

    WEEKLY_AT = 3
    """The quest resets every week at a specific offset
    from the first day of the week.
    """

    MONTHLY_AT = 4
    """The quest resets every month at a specific offset
    from the first day of the month.
    """

    CUSTOM = 5
    """The quest's repetition is determined by a script."""

    ON_COMPLETION = 6
    """The quest resets immediately on completion."""
