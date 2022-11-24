from typing import Protocol

from .models import SteamApp

class IAppDataProvider(Protocol):
    async def get(self, identifier: int) -> SteamApp | None:
        ...

    async def find(self, name: str) -> SteamApp | None:
        ...
