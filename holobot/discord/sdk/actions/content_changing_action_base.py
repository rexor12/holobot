from dataclasses import dataclass, field
from typing import List, Union

from .action_base import ActionBase
from ..models import Embed
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, Layout

@dataclass
class ContentChangingActionBase(ActionBase):
    content: Union[str, Embed]
    components: Union[ComponentBase, List[Layout]] = field(default_factory=lambda: [])