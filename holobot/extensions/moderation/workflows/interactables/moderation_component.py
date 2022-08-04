from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables import Component
from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass(kw_only=True)
class ModerationComponent(Component):
    """Defines a moderation performing component interaction."""

    required_moderator_permissions: ModeratorPermission = ModeratorPermission.NONE
    """Permissions that are required for the invocation."""

    def __str__(self) -> str:
        return f"ModerationComponent({self.identifier})"
