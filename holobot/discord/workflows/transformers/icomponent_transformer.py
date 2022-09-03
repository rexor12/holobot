from typing import Protocol

from hikari import ComponentInteraction
from hikari.api.special_endpoints import ComponentBuilder

from holobot.discord.sdk.workflows.interactables.components import ComponentBase, LayoutBase
from holobot.discord.sdk.workflows.interactables.components.models import ComponentStateBase

class IComponentTransformer(Protocol):
    def transform_component(self, component: ComponentBase) -> ComponentBuilder:
        ...

    def transform_to_root_component(
        self,
        components: ComponentBase | list[LayoutBase]
    ) -> list[ComponentBuilder]:
        ...

    def transform_state(
        self,
        component_type: type[ComponentBase],
        interaction: ComponentInteraction
    ) -> ComponentStateBase:
        ...
