from dataclasses import dataclass
from holobot.discord.sdk.commands import CommandResponse

@dataclass
class UserWarnedResponse(CommandResponse):
    author_id: str = ""
    user_id: str = ""
    reason: str = ""
