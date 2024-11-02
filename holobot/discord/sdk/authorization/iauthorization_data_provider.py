from collections.abc import Awaitable, Iterable
from typing import Protocol

from holobot.discord.sdk.workflows.interactables import Interactable

class IAuthorizationDataProvider(Protocol):
    def is_server_authorized(self, interactable: Interactable, server_id: str) -> Awaitable[bool]:
        ...

    def get_authorized_server_ids(self, interactable: Interactable) -> Awaitable[Iterable[str]]:
        ...
