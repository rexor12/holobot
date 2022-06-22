from ..context_menus.models import MenuItemResponse
from dataclasses import dataclass, field
from holobot.sdk.reactive.models import EventBase
from typing import Any, Optional, Type

@dataclass
class MenuItemExecutedEvent(EventBase):
    menu_item_type: Type[Any] = object
    server_id: Optional[str] = ""
    user_id: str = ""
    response: MenuItemResponse = field(default_factory=MenuItemResponse)
