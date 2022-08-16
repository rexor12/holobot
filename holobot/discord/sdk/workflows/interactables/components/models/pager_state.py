from dataclasses import dataclass
from typing import Any

from .component_state_base import ComponentStateBase

@dataclass(kw_only=True)
class PagerState(ComponentStateBase):
    current_page: int
    """The index of the currently selected page."""

    custom_data: dict[str, Any]
    """Additional data used by extensions."""
