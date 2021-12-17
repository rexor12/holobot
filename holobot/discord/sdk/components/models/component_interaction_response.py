from dataclasses import dataclass, field
from holobot.discord.sdk.actions import ActionBase, DoNothingAction

@dataclass
class ComponentInteractionResponse:
    action: ActionBase = field(default_factory=lambda: DoNothingAction())