from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.general.models import FortuneCookie
from holobot.sdk.database.repositories import IRepository

class IFortuneCookieRepository(IRepository[int, FortuneCookie], Protocol):
    def get_random(self) -> Awaitable[FortuneCookie | None]:
        ...
