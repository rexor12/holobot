from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class UserMutedResponse(InteractionResponse):
    author_id: str = ""
    user_id: str = ""
    reason: str = ""
    duration: Optional[timedelta] = None
