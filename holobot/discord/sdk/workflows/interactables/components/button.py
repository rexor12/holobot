from dataclasses import dataclass, field

from .enums import ComponentStyle
from .interactable_component_base import InteractableComponentBase

@dataclass(kw_only=True)
class Button(InteractableComponentBase):
    text: str | None = None
    style: ComponentStyle = ComponentStyle.PRIMARY
    is_enabled: bool = True
    url: str | None = None

    emoji: int | str | None = None
    """The identifier of a custom emoji or a Unicode emoji itself."""

    custom_data: dict[str, str] = field(default_factory=dict)
