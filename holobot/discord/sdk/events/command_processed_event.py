from dataclasses import dataclass, field

from holobot.sdk.reactive.models import EventBase
from ..workflows.interactables.models import InteractionResponse

@dataclass(frozen=True)
class CommandProcessedEvent(EventBase):
    command_type: type = object
    server_id: str = ""
    user_id: str = ""
    command: str = ""
    group: str | None = None
    subgroup: str | None = None
    response: InteractionResponse = field(default_factory=InteractionResponse)
