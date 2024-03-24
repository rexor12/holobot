from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.sdk.quests.dtos import QuestRewardDescriptor
from holobot.extensions.general.sdk.quests.enums import QuestStatus
from holobot.extensions.general.sdk.quests.models import IQuest, QuestProtoId

class IQuestManager(Protocol):
    def start_quest(
        self,
        server_id: str,
        user_id: str,
        quest_proto_id: QuestProtoId
    ) -> Awaitable[IQuest]:
        ...

    def complete_quest(
        self,
        server_id: str,
        user_id: str,
        quest_proto_id: QuestProtoId
    ) -> Awaitable[QuestRewardDescriptor]:
        ...

    def get_quest_status(
        self,
        server_id: str,
        user_id: str,
        quest_proto_id: QuestProtoId
    ) -> Awaitable[QuestStatus]:
        ...
