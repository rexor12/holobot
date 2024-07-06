from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.steam.models import SteamApp

class ISteamCommunityClient(Protocol):
    def search_apps(self, search_text: str) -> Awaitable[tuple[SteamApp, ...]]:
        ...
