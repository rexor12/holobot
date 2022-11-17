import asyncio
from dataclasses import dataclass, field

from holobot.extensions.google.enums import SearchType
from .search_result_item import SearchResultItem

@dataclass(kw_only=True)
class ExpandingSearchResult:
    query: str
    search_type: SearchType
    current_page: int = 1
    last_page: int = 1
    results_per_page: int = 10
    total_result_count: int = 0
    available_result_count: int = 0
    items: list[SearchResultItem] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
