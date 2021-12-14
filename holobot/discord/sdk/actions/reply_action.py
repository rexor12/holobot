from .action_base import ActionBase
from ..components import Component, StackLayout
from ..models import Embed
from dataclasses import dataclass, field
from typing import List, Union

@dataclass
class ReplyAction(ActionBase):
    """An action that replies to a request with a message."""

    content: Union[str, Embed]
    components: Union[Component, List[StackLayout]] = field(default_factory=lambda: [])
