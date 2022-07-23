from dataclasses import dataclass

from .component_state_base import ComponentStateBase

@dataclass
class EmptyState(ComponentStateBase):
    pass
