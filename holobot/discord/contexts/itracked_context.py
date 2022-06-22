from abc import ABCMeta, abstractmethod
from hikari import PartialInteraction, PartialMessage
from typing import Awaitable, Callable, Optional
from uuid import UUID

class ITrackedContext(metaclass=ABCMeta):
    @property
    @abstractmethod
    def request_id(self) -> UUID:
        ...

    @property
    @abstractmethod
    def context(self) -> PartialInteraction:
        ...

    @abstractmethod
    async def add_message(self, channel_id: str, message_id: str, message: PartialMessage) -> None:
        ...

    @abstractmethod
    async def get_message(self, channel_id: str, message_id: str) -> Optional[PartialMessage]:
        ...

    @abstractmethod
    async def get_or_add_message(self, channel_id: str, message_id: str, factory: Callable[[str, str], Awaitable[PartialMessage]]) -> PartialMessage:
        ...
