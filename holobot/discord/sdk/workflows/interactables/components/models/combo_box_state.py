from dataclasses import dataclass, field
from typing import Sequence

@dataclass
class ComboBoxState:
    selected_values: Sequence[str] = field(default_factory=lambda: [])
