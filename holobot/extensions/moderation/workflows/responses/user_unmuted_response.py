from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class UserUnmutedResponse(InteractionResponse):
    author_id: int = 0
    user_id: int = 0
