from .models import EventBase
from typing import Generic, TypeVar

T = TypeVar("T", bound=EventBase)

class ListenerInterface(Generic[T]):
    async def on_event(self, event: T):
        raise NotImplementedError