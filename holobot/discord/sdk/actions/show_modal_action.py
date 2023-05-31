from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.views import Modal
from .action_base import ActionBase

@dataclass(kw_only=True, frozen=True)
class ShowModalAction(ActionBase):
    """An action that displays a modal to the user."""

    modal: Modal
    """The modal to be displayed."""
