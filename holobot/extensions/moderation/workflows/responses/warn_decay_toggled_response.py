from dataclasses import dataclass
from datetime import timedelta

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class WarnDecayToggledResponse(InteractionResponse):
    author_id: int = 0
    is_enabled: bool = False
    duration: timedelta | None = None
