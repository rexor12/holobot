from dataclasses import dataclass

@dataclass(kw_only=True)
class ItemDisplayInfoBase:
    name: str

@dataclass(kw_only=True)
class CurrencyDisplayInfo(ItemDisplayInfoBase):
    emoji_id: int
    emoji_name: str
    # description: str | None

@dataclass(kw_only=True)
class BadgeDisplayInfo(ItemDisplayInfoBase):
    emoji_id: int
    emoji_name: str
    # description: str | None

@dataclass(kw_only=True)
class BackgroundDisplayInfo(ItemDisplayInfoBase):
    pass
