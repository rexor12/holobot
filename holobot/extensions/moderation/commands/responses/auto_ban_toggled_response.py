from dataclasses import dataclass
from holobot.discord.sdk.commands.models import CommandResponse

@dataclass
class AutoBanToggledResponse(CommandResponse):
    author_id: str = ""
    is_enabled: bool = False
    warn_count: int = 0
