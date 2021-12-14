from .itracked_context import ITrackedContext
from discord import Message
from discord.ext.commands import Context
from discord_slash.context import ComponentContext, MenuContext, SlashContext
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.concurrency import Task
from typing import Awaitable, Callable, Optional, Union
from uuid import UUID

class TrackedContext(ITrackedContext):
    def __init__(self,
        request_id: UUID,
        context: Union[ComponentContext, Context, MenuContext, SlashContext]) -> None:
        super().__init__()
        self.__request_id: UUID = request_id
        self.__context: Union[ComponentContext, Context, MenuContext, SlashContext] = context
        self.__messages: ConcurrentCache[str, ConcurrentCache[str, Message]] = ConcurrentCache()

    @property
    def request_id(self) -> UUID:
        return self.__request_id

    @property
    def context(self) -> Union[ComponentContext, Context, MenuContext, SlashContext]:
        return self.__context

    @property
    def messages(self) -> ConcurrentCache[str, ConcurrentCache[str, Message]]:
        raise NotImplementedError

    async def add_message(self, channel_id: str, message_id: str, message: Message) -> None:
        cache = await self.__messages.get_or_add(channel_id, lambda _: Task.from_result(ConcurrentCache()))
        await cache.add_or_update(
            message_id,
            lambda _: Task.from_result(message),
            lambda _, __: Task.from_result(message)
        )

    async def get_message(self, channel_id: str, message_id: str) -> Optional[Message]:
        cache = await self.__messages.get_or_add(channel_id, lambda _: Task.from_result(ConcurrentCache()))
        return await cache.get(message_id)

    async def get_or_add_message(self, channel_id: str, message_id: str, factory: Callable[[str, str], Awaitable[Message]]) -> Message:
        cache = await self.__messages.get_or_add(channel_id, lambda _: Task.from_result(ConcurrentCache()))
        return await cache.get_or_add2(message_id, lambda mid, cid: factory(cid, mid), channel_id)
