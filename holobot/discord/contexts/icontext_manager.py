from .itracked_context import ITrackedContext
from hikari import PartialInteraction
from holobot.sdk.concurrency import IAsyncDisposable
from uuid import UUID

class IContextManager:
    async def get_context(self, request_id: UUID) -> ITrackedContext:
        raise NotImplementedError

    async def store_context(self, request_id: UUID, context: PartialInteraction) -> None:
        raise NotImplementedError

    async def remove_context(self, request_id: UUID) -> ITrackedContext:
        raise NotImplementedError

    async def register_context(self, request_id: UUID, context: PartialInteraction) -> IAsyncDisposable:
        raise NotImplementedError
