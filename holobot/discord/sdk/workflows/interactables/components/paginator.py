from dataclasses import dataclass, field
from math import ceil
from typing import Any, Dict, Optional

from .layout import Layout

@dataclass
class Paginator(Layout):
    current_page: int = 0
    page_size: Optional[int] = None
    total_count: Optional[int] = None
    has_previous_page: Optional[bool] = None
    has_next_page: Optional[bool] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def is_first_page(self) -> bool:
        return self.current_page == 0

    def is_last_page(self) -> bool:
        if self.total_count is None or self.page_size is None:
            return False

        last_page_index = ceil(self.total_count / self.page_size) - 1
        return self.current_page == last_page_index
