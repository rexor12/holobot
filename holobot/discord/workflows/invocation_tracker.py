from datetime import datetime

from holobot.discord.sdk.workflows.interactables.enums import EntityType
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import UndefinedType
from .iinvocation_tracker import IInvocationTracker

@injectable(IInvocationTracker)
class InvocationTracker(IInvocationTracker):
    def __init__(self) -> None:
        super().__init__()
        self.__cache = ConcurrentCache[EntityType, ConcurrentCache[str, datetime]]()

    async def set_invocation(
        self,
        entity_type: EntityType,
        entity_id: str,
        invoked_at: datetime
    ) -> None:
        entities = await self.__cache.get_or_add3(
            entity_type,
            lambda _: ConcurrentCache()
        )
        await entities.add_or_update3(
            entity_id,
            lambda k, n: n,
            lambda k, i, n: n,
            invoked_at
        )

    async def get_invocation(
        self,
        entity_type: EntityType,
        entity_id: str
    ) -> datetime | None:
        entities = await self.__cache.get(entity_type)
        if not entities:
            return None

        entity = await entities.get(entity_id)
        return entity if entity else None
