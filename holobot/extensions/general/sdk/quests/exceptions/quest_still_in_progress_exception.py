from holobot.extensions.general.sdk.quests.models import QuestProtoId

class QuestStillInProgressException(Exception):
    @property
    def quest_proto_id(self) -> QuestProtoId:
        return self.__quest_proto_id

    def __init__(
        self,
        quest_proto_id: QuestProtoId,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__quest_proto_id = quest_proto_id
