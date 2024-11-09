from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass
class ModeratorPermissionsChangedResponse(InteractionResponse):
    author_id: int = 0
    user_id: int = 0
    permission: ModeratorPermission = ModeratorPermission.NONE
    is_addition: bool = False
