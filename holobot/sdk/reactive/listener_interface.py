from .models import EventBase
from typing import Generic, TypeVar

TEvent = TypeVar("TEvent", bound=EventBase)

class ListenerInterface(Generic[TEvent]):
    async def on_event(self, event: TEvent) -> None:
        raise NotImplementedError
