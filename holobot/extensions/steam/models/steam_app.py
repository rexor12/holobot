from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class SteamApp:
    identifier: int
    name: str
