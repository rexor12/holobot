from typing import Generic, Protocol, TypeVar

from .models import EventBase

TEvent = TypeVar("TEvent", bound=EventBase, contravariant=True)

class IListener(Generic[TEvent], Protocol):
    @property
    def priority(self) -> int:
        """Used to determine the sequence in which listeners are processed.

        When two listeners' priorities are compared, the one
        with the lower priority should be processed first.

        :return: The priority of the listener.
        :rtype: int
        """

        return 0

    async def on_event(self, event: TEvent) -> None:
        ...
