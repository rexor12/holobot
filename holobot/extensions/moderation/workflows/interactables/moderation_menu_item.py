from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables import MenuItem
from .moderation_interactable_mixin import ModerationInteractableMixin

@dataclass(kw_only=True)
class ModerationMenuItem(ModerationInteractableMixin, MenuItem):
    """Defines a moderation performing menu item interaction."""
