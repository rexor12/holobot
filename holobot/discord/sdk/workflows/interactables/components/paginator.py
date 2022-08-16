from dataclasses import dataclass, field
from math import ceil
from typing import Any

from .interactable_layout_base import InteractableLayoutBase

@dataclass(kw_only=True)
class Paginator(InteractableLayoutBase):
    current_page: int = 0
    page_size: int | None = None
    total_count: int | None = None
    has_previous_page: bool | None = None
    has_next_page: bool | None = None
    custom_data: dict[str, Any] = field(default_factory=dict)

    def is_first_page(self) -> bool:
        return self.current_page == 0

    def is_last_page(self) -> bool:
        if self.total_count is None or self.page_size is None:
            return False

        last_page_index = ceil(self.total_count / self.page_size) - 1
        return self.current_page >= last_page_index
