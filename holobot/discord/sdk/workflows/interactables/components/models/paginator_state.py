from dataclasses import dataclass
from typing import Any

from .component_state_base import ComponentStateBase

@dataclass(kw_only=True)
class PaginatorState(ComponentStateBase):
    current_page: int
    """The index of the currently selected page."""

    custom_data: dict[str, str]
    """Additional data used by extensions."""
