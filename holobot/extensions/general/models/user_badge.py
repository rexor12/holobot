from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.general.sdk.badges.models import UserBadgeId
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class UserBadge(AggregateRoot[UserBadgeId]):
    """Represents a badge acquired by a user."""

    unlocked_at: datetime
    """The date and time at which the user acquired the badge."""
