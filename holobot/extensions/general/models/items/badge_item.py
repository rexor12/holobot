from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.general.sdk.badges.models import BadgeId
from .item_base import ItemBase

@dataclass
class BadgeItem(ItemBase):
    """A badge type item."""

    badge_id: BadgeId
    """The identifier of the badge."""

    unlocked_at: datetime
    """The date and time at which the badge was acquired by the user."""
