from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables import Component
from .moderation_interactable_mixin import ModerationInteractableMixin

@dataclass(kw_only=True)
class ModerationComponent(ModerationInteractableMixin, Component):
    """Defines a moderation performing component interaction."""
