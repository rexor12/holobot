from abc import ABCMeta, abstractmethod

from holobot.extensions.google.enums import SearchType
from holobot.extensions.google.models import Language, SearchResult, Translation

class IGoogleClient(metaclass=ABCMeta):
    @abstractmethod
    async def search(
        self,
        search_type: SearchType,
        query: str,
        max_results: int = 1,
        page_index: int = 1
    ) -> SearchResult:
        ...

    @abstractmethod
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None
    ) -> Translation | None:
        ...

    @abstractmethod
    async def get_languages(self) -> dict[str, Language]:
        ...

    @abstractmethod
    async def get_language_by_code(self, code: str) -> Language | None:
        ...
