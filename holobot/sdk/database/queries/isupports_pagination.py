from typing import Protocol

from .paginate_builder import PaginateBuilder

class ISupportsPagination(Protocol):
    def paginate(
        self,
        ordering_column: str,
        page_index: int,
        page_size: int
    ) -> PaginateBuilder:
        ...
