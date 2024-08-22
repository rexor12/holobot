from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class Badge(AggregateRoot[BadgeId]):
    """Represents a badge."""

    created_by: str
    """The identifier of the user who created the badge."""

    created_at: datetime
    """The date and time at which the badge was created."""

    name: str
    """The name of the badge."""

    description: str | None = None
    """An optional description of the badge."""

    emoji_name: str
    """The name of the emoji associated to the badge for use in messages."""

    emoji_id: int
    """The name of the emoji associated to the badge for use in messages."""
