from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass(kw_only=True)
class ModerationInteractableMixin(Interactable):
    """Defines attributes common to moderation interactions."""

    required_moderator_permissions: ModeratorPermission = ModeratorPermission.NONE
    """Permissions that are required for the invocation."""
