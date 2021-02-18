from typing import Generic, TypeVar
from holobot.reactive.models.event_base import EventBase

T = TypeVar("T", bound=EventBase)

class ListenerInterface(Generic[T]):
    async def on_event(self, event: T):
        raise NotImplementedError