from .itracked_context import ITrackedContext
from hikari import PartialInteraction, PartialMessage
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.concurrency import Task
from typing import Awaitable, Callable, Optional
from uuid import UUID

class TrackedContext(ITrackedContext):
    def __init__(self,
        request_id: UUID,
        context: PartialInteraction) -> None:
        super().__init__()
        self.__request_id: UUID = request_id
        self.__context: PartialInteraction = context
        self.__messages: ConcurrentCache[str, ConcurrentCache[str, PartialMessage]] = ConcurrentCache()

    @property
    def request_id(self) -> UUID:
        return self.__request_id

    @property
    def context(self) -> PartialInteraction:
        return self.__context

    @property
    def messages(self) -> ConcurrentCache[str, ConcurrentCache[str, PartialMessage]]:
        raise NotImplementedError

    async def add_message(self, channel_id: str, message_id: str, message: PartialMessage) -> None:
        cache = await self.__messages.get_or_add(channel_id, lambda _: Task.from_result(ConcurrentCache()))
        await cache.add_or_update(
            message_id,
            lambda _: Task.from_result(message),
            lambda _, __: Task.from_result(message)
        )

    async def get_message(self, channel_id: str, message_id: str) -> Optional[PartialMessage]:
        cache = await self.__messages.get_or_add(channel_id, lambda _: Task.from_result(ConcurrentCache()))
        return await cache.get(message_id)

    async def get_or_add_message(self, channel_id: str, message_id: str, factory: Callable[[str, str], Awaitable[PartialMessage]]) -> PartialMessage:
        cache = await self.__messages.get_or_add(channel_id, lambda _: Task.from_result(ConcurrentCache()))
        return await cache.get_or_add2(message_id, lambda mid, cid: factory(cid, mid), channel_id)
