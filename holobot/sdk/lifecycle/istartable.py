from typing import Protocol

class IStartable(Protocol):
    async def start(self):
        ...

    async def stop(self):
        ...
