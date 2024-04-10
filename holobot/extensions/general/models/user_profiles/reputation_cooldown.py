from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class ReputationCooldown(AggregateRoot[str]):
    """Represents a the reputation cooldown data of a user."""

    last_target_user_id: str
    """The identifier of the user that was awarded a reputation point the last time."""

    last_rep_at: datetime
    """The date and time at which the user last awarded a reputation point to someone."""
