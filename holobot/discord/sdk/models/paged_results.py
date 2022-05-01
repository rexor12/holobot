from dataclasses import dataclass
from typing import Generic, Optional, Tuple, TypeVar

T = TypeVar("T")

@dataclass
class PagedResults(Generic[T]):
    results: Tuple[T, ...]
    page_index: int
    page_count: Optional[int] = None
    total_results: Optional[int] = None
