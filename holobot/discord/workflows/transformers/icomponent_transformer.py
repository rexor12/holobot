from abc import ABCMeta, abstractmethod
from typing import Any, Type

from hikari import ComponentInteraction
from hikari.api.special_endpoints import ComponentBuilder

from holobot.discord.sdk.workflows.interactables.components import ComponentBase

class IComponentTransformer(metaclass=ABCMeta):
    @abstractmethod
    def transform_component(self, component: ComponentBase) -> ComponentBuilder:
        ...

    @abstractmethod
    def transform_state(
        self,
        component_type: Type[ComponentBase],
        interaction: ComponentInteraction
    ) -> Any:
        ...
