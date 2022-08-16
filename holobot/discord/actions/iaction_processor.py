from abc import ABCMeta, abstractmethod
from collections.abc import Coroutine
from typing import Any

from hikari import PartialInteraction

from holobot.discord.sdk.actions import ActionBase
from holobot.discord.sdk.actions.enums import DeferType

class IActionProcessor(metaclass=ABCMeta):
    @abstractmethod
    def process(
        self,
        context: PartialInteraction,
        action: ActionBase,
        deferral: DeferType = DeferType.NONE,
        is_ephemeral: bool = False
    ) -> Coroutine[Any, Any, None]:
        ...
