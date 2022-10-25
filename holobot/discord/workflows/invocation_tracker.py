from datetime import datetime, timedelta

from holobot.discord.sdk.workflows.interactables.enums import EntityType
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.ioc.decorators import injectable
from .iinvocation_tracker import IInvocationTracker

@injectable(IInvocationTracker)
class InvocationTracker(IInvocationTracker):
    """A service used for tracking interactable invocations."""

    def __init__(self) -> None:
        super().__init__()
        self.__cache = ConcurrentCache[EntityType, ConcurrentCache[str, datetime]]()

    async def update_invocation(
        self,
        entity_type: EntityType,
        entity_id: str,
        invoked_at: datetime,
        expires_after: timedelta
    ) -> datetime | None:
        entities = await self.__cache.get_or_add3(entity_type, lambda _: ConcurrentCache())
        old_value, _ = await entities.add_or_update3(
            entity_id,
            lambda key, new_value: new_value[0],
            lambda key, old_value, new_value: InvocationTracker.__get_new_value(
                old_value,
                new_value[0],
                new_value[1]
            ),
            (invoked_at, expires_after)
        )

        return old_value if isinstance(old_value, datetime) else None

    @staticmethod
    def __get_new_value(
        last_invoked_at: datetime,
        invoked_at: datetime,
        expires_after: timedelta
    ) -> datetime:
        return (
            last_invoked_at
            if (last_invoked_at + expires_after - invoked_at).total_seconds() > 0
            else invoked_at
        )
