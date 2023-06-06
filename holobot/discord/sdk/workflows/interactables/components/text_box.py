from dataclasses import dataclass, field

from .enums import TextBoxStyle
from .interactable_component_base import InteractableComponentBase

@dataclass(kw_only=True)
class TextBox(InteractableComponentBase):
    label: str
    style: TextBoxStyle = TextBoxStyle.SINGLE_LINE
    placeholder: str | None = None
    default_value: str | None = None
    is_required: bool = False
    min_length: int = 0
    max_length: int = 4000
    custom_data: dict[str, str] = field(default_factory=dict)
