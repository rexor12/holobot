from datetime import timedelta

from holobot.extensions.general.sdk.quests.models import QuestProtoId

class QuestOnCooldownException(Exception):
    @property
    def quest_proto_id(self) -> QuestProtoId:
        return self.__quest_proto_id

    @property
    def time_left(self) -> timedelta:
        return self.__time_left

    def __init__(
        self,
        quest_proto_id: QuestProtoId,
        time_left: timedelta,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__quest_proto_id = quest_proto_id
        self.__time_left = time_left
