from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class UserBannedResponse(InteractionResponse):
    author_id: str = ""
    user_id: str = ""