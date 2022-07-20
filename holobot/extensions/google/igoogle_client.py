from abc import ABCMeta, abstractmethod
from typing import Tuple

from .enums import SearchType
from .models import SearchResult

class IGoogleClient(metaclass=ABCMeta):
    @abstractmethod
    async def search(
        self,
        search_type: SearchType,
        query: str,
        max_results: int = 1
    ) -> Tuple[SearchResult, ...]:
        ...