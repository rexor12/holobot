from dataclasses import dataclass
from holobot.discord.sdk.commands import CommandResponse
from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass
class ModeratorPermissionsChangedResponse(CommandResponse):
    author_id: str = ""
    user_id: str = ""
    permission: ModeratorPermission = ModeratorPermission.NONE
    is_addition: bool = False
