from dataclasses import dataclass, field

@dataclass
class Image:
    byteSize: int = 0

@dataclass
class SearchItem:
    title: str
    link: str
    image: Image = field(default_factory=Image)

@dataclass
class SearchInformation:
    totalResults: int = 0

@dataclass
class SearchResponse:
    searchInformation: SearchInformation = field(default_factory=SearchInformation)
    items: list[SearchItem] = field(default_factory=list)
