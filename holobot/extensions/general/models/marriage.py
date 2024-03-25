from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class Marriage(AggregateRoot[int]):
    """Represents a relationship between two users."""

    identifier: int = -1
    """The identifier of the relationship."""

    server_id: str
    """The identifier of the server on which this relationship exists."""

    user_id1: str
    """The identifier of one of the users."""

    user_id2: str
    """The identifier of the other user."""

    married_at: datetime
    """The date and time at which the relationship was established."""

    level: int = 1
    """The current level of the relationship."""

    last_level_up_at: datetime | None = None
    """The date and time at which the user leveled up last."""

    exp_points: int = 0
    """The experience points the users have gathered so far at the current level."""

    last_activity_at: datetime | None = None
    """The date and time at which the last activity that awards experience points was performed."""

    activity_tier_reset_at: datetime
    """The date and time at which the activity tier was reset to zero."""

    activity_tier: int = 0
    """The currently active activity tier."""

    hug_count: int = 0
    """The number of times the users hugged each other."""

    kiss_count: int = 0
    """The number of times the users kissed each other."""

    pat_count: int = 0
    """The number of times the users patted each other."""

    poke_count: int = 0
    """The number of times the users poked each other."""

    lick_count: int = 0
    """The number of times the users licked each other."""

    bite_count: int = 0
    """The number of times the users bit each other."""

    handhold_count: int = 0
    """The number of times the users held each other's hands."""

    cuddle_count: int = 0
    """The number of times the users cuddled with each other."""

    match_bonus: int = 0
    """The bonus score this marriage gets for the match command."""

    @property
    def total_interactions(self) -> int:
        """Gets the total number of interactions performed.

        :return: The total number of interactions performed.
        :rtype: int
        """

        return (
            self.hug_count
            + self.kiss_count
            + self.pat_count
            + self.poke_count
        )

    def get_spouse(self, user_id: str) -> str:
        """Gets the identifier of the user that isn't the specified one.

        :param user_id: The identifier of the excluded user.
        :type user_id: str
        :return: The spouse of the user.
        :rtype: str
        """

        return self.user_id2 if self.user_id1 == user_id else self.user_id1
