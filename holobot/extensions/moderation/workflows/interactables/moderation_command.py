from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables import Command
from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass(kw_only=True)
class ModerationCommand(Command):
    """Defines a moderation performing slash command interaction."""

    required_moderator_permissions: ModeratorPermission = ModeratorPermission.NONE
    """Permissions that are required for the invocation."""
