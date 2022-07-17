from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables import MenuItem
from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass(kw_only=True)
class ModerationMenuItem(MenuItem):
    """Defines a moderation performing menu item interaction."""

    required_moderator_permissions: ModeratorPermission = ModeratorPermission.NONE
    """Permissions that are required for the invocation."""
