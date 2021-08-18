from dataclasses import dataclass
from datetime import timedelta
from holobot.discord.sdk.commands import CommandResponse
from typing import Optional

@dataclass
class UserMutedResponse(CommandResponse):
    author_id: str = ""
    user_id: str = ""
    reason: str = ""
    duration: Optional[timedelta] = None
