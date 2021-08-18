from dataclasses import dataclass
from holobot.discord.sdk.commands import CommandResponse

@dataclass
class AutoKickToggledResponse(CommandResponse):
    author_id: str = ""
    is_enabled: bool = False
    warn_count: int = 0
