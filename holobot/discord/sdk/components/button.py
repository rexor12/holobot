from .enums import ComponentStyle
from .component import Component
from dataclasses import dataclass
from typing import Optional

@dataclass
class Button(Component):
    text: str
    style: ComponentStyle = ComponentStyle.PRIMARY
    is_enabled: bool = True
    url: Optional[str] = None
