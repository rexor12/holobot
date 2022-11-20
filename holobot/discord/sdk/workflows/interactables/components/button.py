from dataclasses import dataclass

from .enums import ComponentStyle
from .interactable_component_base import InteractableComponentBase

@dataclass(kw_only=True)
class Button(InteractableComponentBase):
    text: str | None = None
    style: ComponentStyle = ComponentStyle.PRIMARY
    is_enabled: bool = True
    url: str | None = None
    emoji_id: str | None = None
