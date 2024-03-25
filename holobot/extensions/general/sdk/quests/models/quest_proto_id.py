from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class QuestProtoId(Identifier):
    server_id: str
    """The identifier of the server the quest prototype belongs to."""

    code: str
    """The unique code of the quest prototype."""

    def __str__(self) -> str:
        return f"QuestProto/{self.server_id}/{self.code}"

    @staticmethod
    def create(server_id: str | None, code: str) -> 'QuestProtoId':
        return QuestProtoId(
            server_id=server_id or "0",
            code=code
        )
