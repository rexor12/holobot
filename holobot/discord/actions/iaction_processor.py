from abc import ABCMeta, abstractmethod
from hikari import PartialInteraction
from holobot.discord.sdk.actions import ActionBase
from holobot.discord.sdk.actions.enums import DeferType

class IActionProcessor(metaclass=ABCMeta):
    @abstractmethod
    async def process(
        self,
        context: PartialInteraction,
        action: ActionBase,
        deferral: DeferType
    ) -> None:
        ...
