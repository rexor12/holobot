from typing import Protocol

from .enums import Order
from .paginate_builder import PaginateBuilder

class ISupportsPagination(Protocol):
    def paginate(
        self,
        ordering_columns: tuple[tuple[str, Order], ...],
        page_index: int,
        page_size: int
    ) -> PaginateBuilder:
        ...
