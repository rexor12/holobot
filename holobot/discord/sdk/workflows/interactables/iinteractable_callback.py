from abc import ABCMeta, abstractmethod
from typing import Any, Coroutine

from holobot.discord.sdk.models import InteractionContext

class IInteractableCallback(metaclass=ABCMeta):
    # TODO The last param of the coroutine should be a common denominator InteractableResponse.
    # TODO The workflow argument should be IWorkflow, but it's Any to avoid a circular dependency.
    @abstractmethod
    def __call__(
        self,
        workflow: Any,
        context: InteractionContext,
        **arguments
    ) -> Coroutine[Any, Any, Any]:
        ...
