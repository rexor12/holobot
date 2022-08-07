from ..models import ExternalGiveawayItem
from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple

class IExternalGiveawayItemRepository(metaclass=ABCMeta):
    @abstractmethod
    async def count(self, user_id: str) -> int:
        ...

    @abstractmethod
    async def get(self, item_id: int) -> Optional[ExternalGiveawayItem]:
        ...

    @abstractmethod
    async def get_many(
        self,
        start_offset: int,
        page_size: int,
        item_type: str,
        active_only: bool = True) -> Tuple[ExternalGiveawayItem, ...]:
        ...

    @abstractmethod
    async def exists(self, url: str, active_only: bool = True) -> bool:
        ...

    @abstractmethod
    async def store(self, item: ExternalGiveawayItem) -> None:
        ...

    @abstractmethod
    async def delete(self, item_id: int) -> None:
        ...
