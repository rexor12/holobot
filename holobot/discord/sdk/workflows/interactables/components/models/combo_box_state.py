from collections.abc import Sequence
from dataclasses import dataclass, field

from .component_state_base import ComponentStateBase

@dataclass(kw_only=True)
class ComboBoxState(ComponentStateBase):
    selected_values: Sequence[str] = field(default_factory=lambda: [])
