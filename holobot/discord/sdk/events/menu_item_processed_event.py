from dataclasses import dataclass, field
from typing import Any, Type

from ..workflows.interactables.models import InteractionResponse
from holobot.sdk.reactive.models import EventBase

@dataclass
class MenuItemProcessedEvent(EventBase):
    menu_item_type: Type[Any] = object
    server_id: str | None = ""
    user_id: str = ""
    response: InteractionResponse = field(default_factory=InteractionResponse)
