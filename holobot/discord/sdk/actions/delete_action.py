from dataclasses import dataclass

from .content_changing_action_base import ContentChangingActionBase

@dataclass(kw_only=True, frozen=True)
class DeleteAction(ContentChangingActionBase):
    """An action that deletes the initial response.

    This is useful when you don't want the reply-like information
    to appear above the response so as to hide the command usage.

    The response must be deferred in order for this to work;
    otherwise, an interaction failure is reported to the user.
    """
