from typing import Protocol

from holobot.extensions.steam.models import SteamApp

class ISteamCommunityClient(Protocol):
    async def search_apps(self, name: str) -> tuple[SteamApp, ...]:
        ...
