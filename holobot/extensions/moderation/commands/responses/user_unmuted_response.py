from dataclasses import dataclass
from holobot.discord.sdk.commands import CommandResponse

@dataclass
class UserUnmutedResponse(CommandResponse):
    author_id: str = ""
    user_id: str = ""
