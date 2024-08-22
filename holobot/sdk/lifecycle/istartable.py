from collections.abc import Awaitable
from typing import Protocol

class IStartable(Protocol):
    @property
    def priority(self) -> int:
        ...

    def start(self) -> Awaitable[None]:
        ...

    def stop(self) -> Awaitable[None]:
        ...
