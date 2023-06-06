from collections.abc import Sequence
from dataclasses import dataclass, field

from .component_state_base import ComponentStateBase

@dataclass(kw_only=True)
class RoleSelectorState(ComponentStateBase):
    selected_values: Sequence[str] = field(default_factory=tuple)
    custom_data: dict[str, str] = field(default_factory=dict)
