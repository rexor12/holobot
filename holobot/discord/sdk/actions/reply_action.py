from dataclasses import dataclass

from .content_changing_action_base import ContentChangingActionBase

@dataclass(kw_only=True, frozen=True)
class ReplyAction(ContentChangingActionBase):
    """An action that replies to a request with a message."""
