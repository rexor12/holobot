from dataclasses import dataclass
from typing import Optional

from .enums import ComponentStyle
from .interactable_component_base import InteractableComponentBase

@dataclass(kw_only=True)
class Button(InteractableComponentBase):
    text: str
    style: ComponentStyle = ComponentStyle.PRIMARY
    is_enabled: bool = True
    url: Optional[str] = None
