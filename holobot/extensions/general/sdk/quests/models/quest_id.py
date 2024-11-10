from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class QuestId(Identifier):
    server_id: int
    """The identifier of the server the quest belongs to."""

    quest_proto_code: str
    """The code of the associated quest prototype."""

    user_id: int
    """The identifier of the owning user."""

    def __str__(self) -> str:
        return f"Quest/{self.server_id}/{self.user_id}/{self.quest_proto_code}"

    @staticmethod
    def create(quest_proto_code: str, server_id: int | None, user_id: int) -> 'QuestId':
        return QuestId(
            server_id=server_id or 0,
            quest_proto_code=quest_proto_code,
            user_id=user_id
        )
