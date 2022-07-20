from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class LogChannelToggledResponse(InteractionResponse):
    author_id: str = ""
    is_enabled: bool = False
    channel_id: str = ""
