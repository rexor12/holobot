from dataclasses import dataclass, field
from typing import Any, Optional, Type

from ..workflows.interactables.models import MenuItemResponse
from holobot.sdk.reactive.models import EventBase

@dataclass
class MenuItemExecutedEvent(EventBase):
    menu_item_type: Type[Any] = object
    server_id: Optional[str] = ""
    user_id: str = ""
    response: MenuItemResponse = field(default_factory=MenuItemResponse)
