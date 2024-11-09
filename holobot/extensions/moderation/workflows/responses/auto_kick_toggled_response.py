from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class AutoKickToggledResponse(InteractionResponse):
    author_id: int = 0
    is_enabled: bool = False
    warn_count: int = 0
