from dataclasses import dataclass, field
from typing import Any, Type

from holobot.sdk.reactive.models import EventBase
from ..workflows.interactables.models import InteractionResponse

@dataclass(frozen=True)
class CommandProcessedEvent(EventBase):
    command_type: Type[Any] = object
    server_id: str = ""
    user_id: str = ""
    command: str = ""
    group: str | None = None
    subgroup: str | None = None
    response: InteractionResponse = field(default_factory=InteractionResponse)
