from .itracked_context import ITrackedContext
from discord.ext.commands import Context
from discord_slash.context import ComponentContext, MenuContext, SlashContext
from holobot.sdk.concurrency import IAsyncDisposable
from typing import Union
from uuid import UUID

class IContextManager:
    async def get_context(self, request_id: UUID) -> ITrackedContext:
        raise NotImplementedError

    async def store_context(self, request_id: UUID, context: Union[ComponentContext, Context, MenuContext, SlashContext]) -> None:
        raise NotImplementedError

    async def remove_context(self, request_id: UUID) -> ITrackedContext:
        raise NotImplementedError

    async def register_context(self, request_id: UUID, context: Union[ComponentContext, Context, MenuContext, SlashContext]) -> IAsyncDisposable:
        raise NotImplementedError
