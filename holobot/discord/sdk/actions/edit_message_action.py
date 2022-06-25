from .content_changing_action_base import ContentChangingActionBase
from dataclasses import dataclass

@dataclass
class EditMessageAction(ContentChangingActionBase):
    """An action that edits the interaction's message."""
