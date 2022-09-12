from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables import Command
from .moderation_interactable_mixin import ModerationInteractableMixin

@dataclass(kw_only=True)
class ModerationCommand(ModerationInteractableMixin, Command):
    """Defines a moderation performing slash command interaction."""
