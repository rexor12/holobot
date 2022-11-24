from dataclasses import dataclass, field

from .steam_app import SteamApp

@dataclass
class SearchResult:
    items: list[SteamApp] = field(default_factory=list)
