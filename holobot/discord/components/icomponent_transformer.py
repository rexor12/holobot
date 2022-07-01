from abc import ABCMeta, abstractmethod
from hikari import ComponentInteraction
from hikari.api.special_endpoints import ComponentBuilder
from holobot.discord.sdk.components import Component
from typing import Any, Type

class IComponentTransformer(metaclass=ABCMeta):
    @abstractmethod
    def transform_component(self, component: Component) -> ComponentBuilder:
        ...

    @abstractmethod
    def transform_state(
        self,
        component_type: Type[Component],
        interaction: ComponentInteraction
    ) -> Any:
        ...
