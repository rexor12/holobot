from collections.abc import Awaitable, Iterable
from typing import Protocol

from holobot.discord.authorization.models import (
    InteractableAuthorization, InteractableAuthorizationId
)
from holobot.sdk.database.repositories import IRepository

class IInteractableAuthorizationRepository(
    IRepository[InteractableAuthorizationId, InteractableAuthorization],
    Protocol
):
    def has_authorization(
        self,
        server_id: str,
        interactable_id: str
    ) -> Awaitable[bool | None]:
        ...

    def get_authorized_server_ids(
        self,
        interactable_id: str
    ) -> Awaitable[Iterable[str]]:
        ...
