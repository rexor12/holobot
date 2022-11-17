from dataclasses import dataclass

@dataclass
class SearchResultItem:
    title: str
    link: str
    fileSize: int
