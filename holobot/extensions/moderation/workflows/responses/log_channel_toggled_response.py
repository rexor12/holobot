from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class LogChannelToggledResponse(InteractionResponse):
    author_id: int = 0
    is_enabled: bool = False
    channel_id: int = 0
