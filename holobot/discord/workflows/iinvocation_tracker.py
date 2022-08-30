from datetime import datetime
from typing import Protocol

from holobot.discord.sdk.workflows.interactables.enums import EntityType

class IInvocationTracker(Protocol):
    async def set_invocation(
        self,
        entity_type: EntityType,
        entity_id: str,
        invoked_at: datetime
    ) -> None:
        ...

    async def get_invocation(
        self,
        entity_type: EntityType,
        entity_id: str
    ) -> datetime | None:
        ...
