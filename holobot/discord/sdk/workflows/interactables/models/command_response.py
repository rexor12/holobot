from dataclasses import dataclass, field

from holobot.discord.sdk.actions import ActionBase, DoNothingAction

@dataclass
class CommandResponse:
    """Determines the action to be executed as the response of the interaction."""

    action: ActionBase = field(default_factory=DoNothingAction)
    """The action to be executed."""
