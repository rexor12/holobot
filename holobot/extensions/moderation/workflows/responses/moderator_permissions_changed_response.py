from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass
class ModeratorPermissionsChangedResponse(InteractionResponse):
    author_id: str = ""
    user_id: str = ""
    permission: ModeratorPermission = ModeratorPermission.NONE
    is_addition: bool = False
