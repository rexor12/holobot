from .component_base import ComponentBase
from dataclasses import dataclass, field

@dataclass(kw_only=True)
class Layout(ComponentBase):
    children: list[ComponentBase] = field(default_factory=lambda: [])
