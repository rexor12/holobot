from .action_base import ActionBase
from ..models import Embed
from dataclasses import dataclass
from typing import Union

@dataclass
class ReplyAction(ActionBase):
    """An action that replies to a request with a message."""

    content: Union[str, Embed]
