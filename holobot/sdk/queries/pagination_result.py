from dataclasses import dataclass, field
from collections.abc import Sequence
from typing import Generic, TypeVar

TItem = TypeVar("TItem")

@dataclass(frozen=True)
class PaginationResult(Generic[TItem]):
    """Represents the results of a pagination query."""

    page_index: int
    """The zero-based index of the current page."""

    page_size: int
    """The maximum number of items on a single page."""

    total_count: int
    """The total number of items matching the query."""

    items: Sequence[TItem] = field(default_factory=list)
    """The items of the current page."""
