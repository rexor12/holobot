from typing import Protocol

class IWaifuPicsClient(Protocol):
    async def get_batch(
        self,
        category: str
    ) -> tuple[str, ...]:
        ...
