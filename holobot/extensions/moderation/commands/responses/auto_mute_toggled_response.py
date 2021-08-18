from dataclasses import dataclass
from datetime import timedelta
from holobot.discord.sdk.commands import CommandResponse
from typing import Optional

@dataclass
class AutoMuteToggledResponse(CommandResponse):
    author_id: str = ""
    is_enabled: bool = False
    warn_count: int = 0
    duration: Optional[timedelta] = None
