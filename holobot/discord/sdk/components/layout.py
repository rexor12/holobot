from .component import Component
from dataclasses import dataclass, field
from typing import List

@dataclass
class Layout(Component):
    children: List[Component] = field(default_factory=lambda: [])
