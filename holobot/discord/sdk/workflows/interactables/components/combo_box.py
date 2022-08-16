from collections.abc import Sequence
from dataclasses import dataclass, field

from .combo_box_item import ComboBoxItem
from .interactable_component_base import InteractableComponentBase

@dataclass(kw_only=True)
class ComboBox(InteractableComponentBase):
    items: Sequence[ComboBoxItem] = field(default_factory=lambda: [])
    placeholder: str | None = None
    selection_count_min: int = 1
    selection_count_max: int = 1
    is_enabled: bool = True
