from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.general.sdk.badges.models import BadgeId
from .item_storage_model_base import ItemStorageModelBase

@dataclass(kw_only=True)
class BadgeItemStorageModel(ItemStorageModelBase):
    badge_id: BadgeId
    unlocked_at: datetime
