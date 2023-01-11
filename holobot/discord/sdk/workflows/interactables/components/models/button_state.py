from dataclasses import dataclass
from typing import Any

from .component_state_base import ComponentStateBase

@dataclass(kw_only=True)
class ButtonState(ComponentStateBase):
    custom_data: dict[str, Any]
    """Additional data used by extensions."""
