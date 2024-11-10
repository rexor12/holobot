from dataclasses import dataclass, field

from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.sdk.reactive.models import EventBase
from ..workflows.interactables.models import InteractionResponse

@dataclass(kw_only=True, frozen=True)
class MenuItemProcessedEvent(EventBase):
    interactable: Interactable
    server_id: int | None = None
    channel_id: int | None = None
    user_id: int = 0
    response: InteractionResponse = field(default_factory=InteractionResponse)
