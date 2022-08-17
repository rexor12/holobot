from typing import Protocol

from holobot.extensions.giveaways.models import ExternalGiveawayItem, ExternalGiveawayItemMetadata
from holobot.sdk.queries import PaginationResult

class IExternalGiveawayItemRepository(Protocol):
    async def count(self, user_id: str) -> int:
        ...

    async def get(self, item_id: int) -> ExternalGiveawayItem | None:
        ...

    async def get_many(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        active_only: bool = True
    ) -> PaginationResult[ExternalGiveawayItem]:
        ...

    async def get_metadatas(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        active_only: bool = True
    ) -> PaginationResult[ExternalGiveawayItemMetadata]:
        ...

    async def exists(self, url: str, active_only: bool = True) -> bool:
        ...

    async def store(self, item: ExternalGiveawayItem) -> None:
        ...

    async def delete(self, item_id: int) -> None:
        ...

    async def delete_expired(self) -> int:
        ...
