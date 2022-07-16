from abc import ABCMeta, abstractmethod
from typing import Any, Coroutine, Generic, TypeVar

from hikari import MessageResponseMixin

TInteraction = TypeVar("TInteraction", bound=MessageResponseMixin, contravariant=True)

class IInteractionProcessor(Generic[TInteraction], metaclass=ABCMeta):
    """Interface for an interaction processor."""

    @abstractmethod
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
