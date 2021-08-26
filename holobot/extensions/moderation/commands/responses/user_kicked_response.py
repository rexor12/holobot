from dataclasses import dataclass
from holobot.discord.sdk.commands.models import CommandResponse

@dataclass
class UserKickedResponse(CommandResponse):
    author_id: str = ""
    user_id: str = ""
    reason: str = ""
