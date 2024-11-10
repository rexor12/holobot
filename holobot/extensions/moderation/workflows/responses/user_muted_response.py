from dataclasses import dataclass
from datetime import timedelta

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class UserMutedResponse(InteractionResponse):
    author_id: int = 0
    user_id: int = 0
    reason: str = ""
    duration: timedelta | None = None
