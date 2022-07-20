from typing import Any, Coroutine, Generic, Protocol, TypeVar

from hikari import MessageResponseMixin

TInteraction = TypeVar("TInteraction", bound=MessageResponseMixin, contravariant=True)

class IInteractionProcessor(Generic[TInteraction], Protocol):
    """Interface for an interaction processor."""

    def process(self, interaction: TInteraction) -> Coroutine[Any, Any, None]:
        """Processes the specified interaction by invoking
        an associated workflow handler.

        If the interaction is invalid (eg. there is no associated workflow)
        then an error response is generated for the user.

        :param interaction: The interaction to be processed.
        :type interaction: TInteraction
        :return: An awaitable that represents the operation.
        :rtype: Coroutine[Any, Any, None]
        """
        ...
