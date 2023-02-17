from collections.abc import Awaitable
from typing import Protocol

from holobot.extensions.giveaways.models import ExternalGiveawayItem, ExternalGiveawayItemMetadata
from holobot.sdk.database.repositories import IRepository
from holobot.sdk.queries import PaginationResult

class IExternalGiveawayItemRepository(
    IRepository[int, ExternalGiveawayItem],
    Protocol
):
    def get_many(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        active_only: bool = True
    ) -> Awaitable[PaginationResult[ExternalGiveawayItem]]:
        ...

    def get_metadatas(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        active_only: bool = True
    ) -> Awaitable[PaginationResult[ExternalGiveawayItemMetadata]]:
        ...

    def exists(self, url: str, active_only: bool = True) -> Awaitable[bool]:
        ...

    def delete_expired(self) -> Awaitable[int]:
        ...
