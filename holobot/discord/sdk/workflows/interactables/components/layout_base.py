from dataclasses import dataclass, field

from .component_base import ComponentBase

@dataclass(kw_only=True)
class LayoutBase(ComponentBase):
    children: list[ComponentBase] = field(default_factory=list)
