from dataclasses import dataclass, field
from typing import Any, Sequence

@dataclass(frozen=True)
class PaginationResult:
    """Represents the results of a pagination query."""

    page_index: int
    """The zero-based index of the current page."""

    page_size: int
    """The maximum number of records on a single page."""

    total_count: int
    """The total number of records matching the query."""

    records: Sequence[dict[str, Any]] = field(default_factory=list)
    """The records of the current page."""
