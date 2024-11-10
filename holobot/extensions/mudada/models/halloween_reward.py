from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class HalloweenReward(AggregateRoot[int]):
    last_update_at: datetime
    """The date and time at which the reward was last acquired by the user."""

    last_reward_tier: int
    """The reward tier the user received the last time."""

    is_tricked: bool
    """Whether the user was tricked the last time, thus obtaining no rewards."""
