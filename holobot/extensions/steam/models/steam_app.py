from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class SteamApp:
    identifier: str
    name: str
    logo_url: str | None = None
