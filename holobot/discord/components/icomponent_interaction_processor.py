from abc import ABCMeta, abstractmethod
from hikari import ComponentInteraction

class IComponentInteractionProcessor(metaclass=ABCMeta):
    @abstractmethod
    async def process(self, interaction: ComponentInteraction) -> None:
        ...
