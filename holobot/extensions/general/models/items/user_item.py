from dataclasses import dataclass

from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.sdk.database.entities import AggregateRoot
from .item_base import ItemBase

@dataclass(kw_only=True)
class UserItem(AggregateRoot[UserItemId]):
    """Represents an item acquired by a user."""

    item: ItemBase
