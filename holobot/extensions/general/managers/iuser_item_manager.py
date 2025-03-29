from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.enums import GrantItemOutcome
from holobot.extensions.general.models.items import ItemBase, ItemDisplayInfoBase, UserItem
from holobot.extensions.general.sdk.quests.models import QuestRewardBase

class IUserItemManager(Protocol):
    def grant_item(
        self,
        server_id: int,
        user_id: int,
        item: ItemBase
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        ...

    def try_grant_quest_reward(
        self,
        server_id: int,
        user_id: int,
        quest_reward: QuestRewardBase
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        ...

    def get_item_display_info(
        self,
        item: ItemBase
    ) -> Awaitable[ItemDisplayInfoBase]:
        ...
