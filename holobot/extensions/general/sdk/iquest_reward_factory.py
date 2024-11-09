from collections.abc import Awaitable, Iterable
from typing import Protocol

from holobot.extensions.general.sdk.quests.models import QuestRewardBase

class IQuestRewardFactory(Protocol):
    @property
    def relevant_server_ids(self) -> tuple[int, ...]:
        ...

    @property
    def relevant_quest_codes(self) -> tuple[str, ...]:
        ...

    def create_quest_rewards(
        self,
        quest_code: str,
        server_id: int,
        user_id: int
    ) -> Awaitable[Iterable[QuestRewardBase]]:
        ...
