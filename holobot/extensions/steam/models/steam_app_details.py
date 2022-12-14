from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class SteamAppDetails:
    identifier: str
    name: str
    required_age: int
    is_free: bool
    short_description: str
    screenshot_urls: tuple[str, ...]
