from abc import ABCMeta, abstractmethod
from hikari import CommandInteraction

class IMenuItemProcessor(metaclass=ABCMeta):
    @abstractmethod
    async def process(self, interaction: CommandInteraction) -> None:
        ...
