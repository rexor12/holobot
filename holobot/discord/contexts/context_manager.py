from .icontext_manager import IContextManager
from .itracked_context import ITrackedContext
from .tracked_context import TrackedContext
from hikari import PartialInteraction
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.concurrency import AsyncAnonymousDisposable, IAsyncDisposable, Task
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import assert_not_none
from uuid import UUID

@injectable(IContextManager)
class ContextManager(IContextManager):
    def __init__(self) -> None:
        super().__init__()
        self.__cache: ConcurrentCache[UUID, TrackedContext] = ConcurrentCache()

    async def get_context(self, request_id: UUID) -> ITrackedContext:
        assert_not_none(request_id, "request_id")

        if not (context := await self.__cache.get(request_id)):
            raise ArgumentError("request_id", "No context exists for the specified request ID.")
        return context

    async def store_context(self, request_id: UUID, context: PartialInteraction) -> None:
        assert_not_none(request_id, "request_id")
        assert_not_none(context, "context")

        await self.__cache.add3(
            request_id,
            lambda _, rid, ctx: Task.from_result(TrackedContext(rid, ctx)),
            request_id,
            context)

    async def remove_context(self, request_id: UUID) -> ITrackedContext:
        return await self.__cache.remove(request_id)

    async def register_context(self, request_id: UUID, context: PartialInteraction) -> IAsyncDisposable:
        assert_not_none(request_id, "request_id")
        assert_not_none(context, "context")

        await self.__cache.add3(
            request_id,
            lambda _, rid, ctx: Task.from_result(TrackedContext(rid, ctx)),
            request_id,
            context
        )

        return AsyncAnonymousDisposable(lambda: self.remove_context(request_id))
