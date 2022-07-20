from typing import Generic, Protocol, TypeVar

from .models import EventBase

TEvent = TypeVar("TEvent", bound=EventBase, contravariant=True)

class IListener(Generic[TEvent], Protocol):
    async def on_event(self, event: TEvent) -> None:
        ...
