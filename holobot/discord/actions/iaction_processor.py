from abc import ABCMeta, abstractmethod
from hikari import PartialInteraction
from holobot.discord.sdk.actions import ActionBase

class IActionProcessor(metaclass=ABCMeta):
    @abstractmethod
    async def process(self, context: PartialInteraction, action: ActionBase) -> None:
        ...
