from datetime import datetime, timedelta
from typing import Protocol

from holobot.discord.sdk.workflows.interactables.enums import EntityType

class IInvocationTracker(Protocol):
    """Interface for a service used for tracking interactable invocations."""

    async def update_invocation(
        self,
        entity_type: EntityType,
        entity_id: str,
        invoked_at: datetime,
        expires_after: timedelta
    ) -> datetime | None:
        """Updates the invocation tracking for the specified entity.

        :param entity_type: The type of the entity.
        :type entity_type: EntityType
        :param entity_id: The identifier of the entity.
        :type entity_id: str
        :param invoked_at: The date and time at which the invocation occurred.
        :type invoked_at: datetime
        :param expires_after: The duration after which the tracking expires.
        :type expires_after: timedelta
        :return: If available, the date and time of the last invocation.
        :rtype: datetime | None
        """
        ...
