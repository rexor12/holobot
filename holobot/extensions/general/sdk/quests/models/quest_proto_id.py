from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier
from holobot.sdk.utils.hash_utils import combine2

@dataclass(kw_only=True)
class QuestProtoId(Identifier):
    server_id: int
    """The identifier of the server the quest prototype belongs to."""

    code: str
    """The unique code of the quest prototype."""

    def __str__(self) -> str:
        return f"QuestProto/{self.server_id}/{self.code}"

    def __eq__(self, value: object) -> bool:
        if value == self:
            return True
        if not isinstance(value, QuestProtoId):
            return False

        return (
            value.server_id == self.server_id
            and value.code == self.code
        )

    def __hash__(self) -> int:
        return combine2(
            self.server_id,
            self.code
        )

    @staticmethod
    def create(server_id: int | None, code: str) -> 'QuestProtoId':
        return QuestProtoId(
            server_id=server_id or 0,
            code=code
        )
