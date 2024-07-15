from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class BadgeId(Identifier):
    server_id: str
    """The identifier of the server the badge belongs to.

    Should be set to "0" if it's a global badge.
    """

    badge_id: int
    """The server-local identifier of the badge."""

    def __str__(self) -> str:
        return f"Badge/{self.server_id}/{self.badge_id}"

    @staticmethod
    def create(server_id: str, badge_id: int) -> 'BadgeId':
        return BadgeId(
            server_id=server_id,
            badge_id=badge_id
        )
