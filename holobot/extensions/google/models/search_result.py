from dataclasses import dataclass, field

from .search_result_item import SearchResultItem

@dataclass(kw_only=True)
class SearchResult:
    total_result_count: int = 0
    items: list[SearchResultItem] = field(default_factory=list)
