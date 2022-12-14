from typing import Protocol

from holobot.extensions.steam.models import SteamAppDetails

class ISteamAppDetailsClient(Protocol):
    async def get_app_details(self, identifier: str) -> SteamAppDetails | None:
        ...
