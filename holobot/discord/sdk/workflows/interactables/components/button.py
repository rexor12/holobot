from .enums import ComponentStyle
from .component_base import ComponentBase
from dataclasses import dataclass
from typing import Optional

@dataclass
class Button(ComponentBase):
    text: str
    style: ComponentStyle = ComponentStyle.PRIMARY
    is_enabled: bool = True
    url: Optional[str] = None
