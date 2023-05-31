from dataclasses import dataclass, field

from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.sdk.reactive.models import EventBase
from ..workflows.interactables.models import InteractionResponse

@dataclass(kw_only=True, frozen=True)
class ModalProcessedEvent(EventBase):
    interactable: Interactable
    server_id: str | None = ""
    channel_id: str | None = ""
    user_id: str = ""
    response: InteractionResponse = field(default_factory=InteractionResponse)
