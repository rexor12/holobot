from .enums import SearchType
from .models import SearchResult
from typing import Tuple

class GoogleClientInterface:
    async def search(self, search_type: SearchType, query: str, max_results: int = 1) -> Tuple[SearchResult, ...]:
        raise NotImplementedError
