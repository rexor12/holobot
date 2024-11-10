from dataclasses import dataclass, field
from typing import Any

from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.sdk.reactive.models import EventBase
from ..workflows.interactables.models import InteractionResponse

@dataclass(kw_only=True, frozen=True)
class CommandProcessedEvent(EventBase):
    interactable: Interactable
    server_id: int | None = None
    channel_id: int = 0
    user_id: int = 0
    arguments: dict[str, Any] = field(default_factory=dict)
    response: InteractionResponse = field(default_factory=InteractionResponse)
