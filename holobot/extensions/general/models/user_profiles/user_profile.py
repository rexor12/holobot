from dataclasses import dataclass, field
from typing import ClassVar

from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.sdk.collections import Inventory
from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class UserProfile(AggregateRoot[int]):
    """Represents a user's profile."""

    MAX_BADGE_COUNT: ClassVar[int] = 8
    """The maximum number of badges a user can set up for display."""

    reputation_points: int = 0
    """The number of reputation points the user has."""

    background_image_code: str | None = None
    """The code of the background image set for the user's profile."""

    show_badges: bool = True
    """Whether the badges should be displayed on the user's profile."""

    badges: Inventory[BadgeId] = field(default_factory=lambda: Inventory(UserProfile.MAX_BADGE_COUNT))
    """The identifiers of the badges to be displayed on the user's profile."""
