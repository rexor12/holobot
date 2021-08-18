from dataclasses import dataclass
from datetime import timedelta
from holobot.discord.sdk.commands import CommandResponse
from typing import Optional

@dataclass
class WarnDecayToggledResponse(CommandResponse):
    author_id: str = ""
    is_enabled: bool = False
    duration: Optional[timedelta] = None
