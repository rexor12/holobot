from dataclasses import dataclass

from holobot.sdk.utils.type_utils import UNDEFINED, UndefinedType
from .content_changing_action_base import ContentChangingActionBase

@dataclass(kw_only=True, frozen=True)
class ReplyAction(ContentChangingActionBase):
    """An action that replies to a request with a message."""

    is_ephemeral: bool | UndefinedType = UNDEFINED
    """Whether an ephemeral message should be created.

    When specified, it overrides the associated interactable's preferences
    if and only if the response is not deferred. In the case of a deferred response,
    the final response cannot be different from the initial response.
    """
