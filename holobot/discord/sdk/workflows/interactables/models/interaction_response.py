from dataclasses import dataclass, field

from holobot.discord.sdk.actions import ActionBase, DoNothingAction

@dataclass
class InteractionResponse:
    """Describes how the application should respond to an interaction."""

    action: ActionBase = field(default_factory=lambda: DoNothingAction())
    """The action to be executed."""
