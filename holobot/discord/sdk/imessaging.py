from collections.abc import Awaitable
from typing import Protocol

from .models.embed import Embed
from .workflows.interactables.components import ComponentBase, LayoutBase

class IMessaging(Protocol):
    def send_private_message(self, user_id: int, message: str) -> Awaitable[None]:
        ...

    def send_channel_message(
        self,
        server_id: int,
        channel_id: int,
        thread_id: int | None,
        content: str | Embed,
        components: ComponentBase | list[LayoutBase] | None = None,
        *,
        suppress_user_mentions: bool = False
    ) -> Awaitable[int]:
        ...

    def crosspost_message(
        self,
        server_id: int,
        channel_id: int,
        message_id: int
    ) -> Awaitable[None]:
        ...

    def delete_message(self, channel_id: int, message_id: int) -> Awaitable[None]:
        ...
