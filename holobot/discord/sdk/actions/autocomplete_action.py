from dataclasses import dataclass, field

from holobot.discord.sdk.models import AutocompleteChoice
from .action_base import ActionBase

@dataclass(kw_only=True, frozen=True)
class AutocompleteAction(ActionBase):
    """An action for responding with the matching choices of an autocompletion."""

    choices: list[AutocompleteChoice] = field(default_factory=list)
    """The choices that match the autocompletion."""
