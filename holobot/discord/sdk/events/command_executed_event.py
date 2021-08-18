from ..commands import CommandResponse
from dataclasses import dataclass, field
from holobot.sdk.reactive.models import EventBase
from typing import Any, Optional, Type

@dataclass
class CommandExecutedEvent(EventBase):
    command_type: Type[Any] = object
    server_id: str = ""
    user_id: str = ""
    command: str = ""
    group: Optional[str] = None
    subgroup: Optional[str] = None
    response: CommandResponse = field(default_factory=lambda: CommandResponse())
