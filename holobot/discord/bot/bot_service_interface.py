from collections.abc import Awaitable
from typing import Protocol

class BotServiceInterface(Protocol):
    def start(self) -> Awaitable[None]:
        ...

    def stop(self) -> Awaitable[None]:
        ...
