from typing import Any

class SearchResult:
    def __init__(self, link: str) -> None:
        self.link = link

    @property
    def link(self) -> str:
        return self.__link

    @link.setter
    def link(self, value: str) -> None:
        self.__link = value

    @staticmethod
    def from_json(json: dict[str, Any]) -> 'SearchResult':
        return SearchResult(
            link=json.get("link", "")
        )
