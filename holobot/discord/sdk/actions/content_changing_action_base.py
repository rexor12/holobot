from .action_base import ActionBase
from ..components import Component, Layout
from ..models import Embed
from dataclasses import dataclass, field
from typing import List, Union

@dataclass
class ContentChangingActionBase(ActionBase):
    content: Union[str, Embed]
    components: Union[Component, List[Layout]] = field(default_factory=lambda: [])