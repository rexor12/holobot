from dataclasses import dataclass

from .content_changing_action_base import ContentChangingActionBase

@dataclass(kw_only=True, frozen=True)
class EditMessageAction(ContentChangingActionBase):
    """An action that edits the interaction's message."""
