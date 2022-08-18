from dataclasses import dataclass, field

from holobot.sdk.reactive.models import EventBase
from ..workflows.interactables.models import InteractionResponse

@dataclass
class ComponentProcessedEvent(EventBase):
    component_type: type = object
    server_id: str | None = ""
    user_id: str = ""
    response: InteractionResponse = field(default_factory=InteractionResponse)
