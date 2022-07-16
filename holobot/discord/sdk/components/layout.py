from .component_base import ComponentBase
from dataclasses import dataclass, field
from typing import List

@dataclass
class Layout(ComponentBase):
    children: List[ComponentBase] = field(default_factory=lambda: [])
