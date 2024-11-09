from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class InteractableAuthorizationId(Identifier):
    interactable_id: str
    """The identifier of the interactable."""

    server_id: int
    """The identifier of the server."""

    def __str__(self) -> str:
        return f"InteractableAuthorization/{self.interactable_id}/{self.server_id}"

    @staticmethod
    def create(interactable_id: str, server_id: int) -> 'InteractableAuthorizationId':
        return InteractableAuthorizationId(
            interactable_id=interactable_id,
            server_id=server_id
        )
