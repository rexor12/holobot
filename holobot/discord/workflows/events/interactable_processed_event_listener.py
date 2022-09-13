from datetime import datetime, timezone

from holobot.discord.sdk.events import (
    CommandProcessedEvent, ComponentProcessedEvent, MenuItemProcessedEvent
)
from holobot.discord.workflows import IInvocationTracker
from holobot.discord.workflows.utils import get_entity_id
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener

_EVENT_TYPE = CommandProcessedEvent | ComponentProcessedEvent | MenuItemProcessedEvent

@injectable(IListener[CommandProcessedEvent])
@injectable(IListener[ComponentProcessedEvent])
@injectable(IListener[MenuItemProcessedEvent])
class InteractableProcessedEventListener(IListener[_EVENT_TYPE]):
    def __init__(
        self,
        invocation_tracker: IInvocationTracker
    ) -> None:
        super().__init__()
        self.__invocation_tracker = invocation_tracker

    async def on_event(self, event: _EVENT_TYPE) -> None:
        cooldown = event.interactable.cooldown
        if not cooldown:
            return

        if not (entity_id := get_entity_id(
            event.interactable,
            event.server_id,
            event.channel_id,
            event.user_id
        )):
            return

        await self.__invocation_tracker.set_invocation(
            cooldown.entity_type,
            entity_id,
            datetime.now(timezone.utc)
        )
