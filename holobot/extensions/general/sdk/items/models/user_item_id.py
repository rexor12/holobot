from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier
from holobot.sdk.identification import Holoflake

@dataclass(kw_only=True)
class UserItemId(Identifier):
    server_id: int
    """The identifier of the server the item belongs to.

    Should be set to "0" if it's a globally available item.
    """

    user_id: int
    """The identifier of the owning user."""

    serial_id: Holoflake
    """The identifier of the user item unique within the context
    of the user and the server.

    Multiple user items belonging to different users
    may have the same serial identifiers.
    """

    def __str__(self) -> str:
        return f"UserItem/{self.server_id}/{self.user_id}/{self.serial_id}"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, UserItemId):
            return False

        return (
            self.server_id == value.server_id
            and self.user_id == value.user_id
            and self.serial_id == value.serial_id
        )

    @staticmethod
    def create(server_id: int, user_id: int, serial_id: Holoflake) -> 'UserItemId':
        return UserItemId(
            server_id=server_id,
            user_id=user_id,
            serial_id=serial_id
        )
