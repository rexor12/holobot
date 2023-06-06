from dataclasses import dataclass, field

from .interactable_component_base import InteractableComponentBase

@dataclass(kw_only=True)
class RoleSelector(InteractableComponentBase):
    placeholder: str | None = None
    selection_count_min: int = 1
    selection_count_max: int = 1
    is_enabled: bool = True
    custom_data: dict[str, str] = field(default_factory=dict)
