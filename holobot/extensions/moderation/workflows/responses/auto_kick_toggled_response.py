from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse

@dataclass
class AutoKickToggledResponse(InteractionResponse):
    author_id: str = ""
    is_enabled: bool = False
    warn_count: int = 0
