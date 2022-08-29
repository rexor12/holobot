from typing import Protocol

class IReactionProvider(Protocol):
    async def get(self, category: str) -> str | None:
        ...
