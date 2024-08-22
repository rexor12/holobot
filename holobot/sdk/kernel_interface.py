from collections.abc import Awaitable
from typing import Protocol

class KernelInterface(Protocol):
    def run(self) -> Awaitable[None]:
        ...
