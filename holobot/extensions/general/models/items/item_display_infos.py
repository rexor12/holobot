from dataclasses import dataclass

from holobot.extensions.general.sdk.badges.models import BadgeId

@dataclass(kw_only=True)
class ItemDisplayInfoBase:
    name: str

@dataclass(kw_only=True)
class CurrencyDisplayInfo(ItemDisplayInfoBase):
    currency_id: int
    emoji_id: int
    emoji_name: str
    # description: str | None

@dataclass(kw_only=True)
class BadgeDisplayInfo(ItemDisplayInfoBase):
    badge_id: BadgeId
    emoji_id: int
    emoji_name: str
    # description: str | None

@dataclass(kw_only=True)
class BackgroundDisplayInfo(ItemDisplayInfoBase):
    background_id: int
