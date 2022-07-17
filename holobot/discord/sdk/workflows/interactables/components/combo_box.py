from .combo_box_item import ComboBoxItem
from .component_base import ComponentBase
from dataclasses import dataclass, field
from typing import Optional, Sequence

@dataclass
class ComboBox(ComponentBase):
    items: Sequence[ComboBoxItem] = field(default_factory=lambda: [])
    placeholder: Optional[str] = None
    selection_count_min: int = 1
    selection_count_max: int = 1
    is_enabled: bool = True
