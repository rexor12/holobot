from dataclasses import dataclass
from holobot.discord.sdk.commands.models import CommandResponse

@dataclass
class LogChannelToggledResponse(CommandResponse):
    author_id: str = ""
    is_enabled: bool = False
    channel_id: str = ""
