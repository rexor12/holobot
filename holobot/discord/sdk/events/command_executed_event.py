from dataclasses import dataclass, field
from typing import Any, Optional, Type

from ..workflows.interactables.models import InteractionResponse
from holobot.sdk.reactive.models import EventBase

@dataclass
class CommandExecutedEvent(EventBase):
    command_type: Type[Any] = object
    server_id: str = ""
    user_id: str = ""
    command: str = ""
    group: Optional[str] = None
    subgroup: Optional[str] = None
    response: InteractionResponse = field(default_factory=InteractionResponse)
