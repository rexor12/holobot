from .content_changing_action_base import ContentChangingActionBase
from ..components import Component, Layout
from ..models import Embed
from dataclasses import dataclass, field
from typing import List, Union

@dataclass
class ReplyAction(ContentChangingActionBase):
    """An action that replies to a request with a message."""
