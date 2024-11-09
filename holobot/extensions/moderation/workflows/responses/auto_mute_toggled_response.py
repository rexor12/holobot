from dataclasses import dataclass
from datetime import timedelta

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class AutoMuteToggledResponse(InteractionResponse):
    author_id: int = 0
    is_enabled: bool = False
    warn_count: int = 0
    duration: timedelta | None = None
