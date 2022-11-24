from typing import Protocol

from holobot.extensions.steam.models import SteamApp

class ISteamAppsClient(Protocol):
    async def get_app_list(self) -> tuple[SteamApp, ...]:
        ...
