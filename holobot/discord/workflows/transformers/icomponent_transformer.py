from typing import Protocol

from hikari import ComponentInteraction, ModalInteraction
from hikari.api.special_endpoints import ComponentBuilder, ModalActionRowBuilder

from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, ComponentStateBase, LayoutBase
)
from holobot.discord.sdk.workflows.interactables.views import Modal, ModalState

class IComponentTransformer(Protocol):
    def transform_control(
        self,
        components: ComponentBase | list[LayoutBase]
    ) -> list[ComponentBuilder]:
        ...

    def transform_control_state(
        self,
        component_type: type[ComponentBase],
        interaction: ComponentInteraction
    ) -> ComponentStateBase:
        ...

    def transform_modal(
        self,
        view: Modal
    ) -> list[ModalActionRowBuilder]:
        ...

    def transform_modal_state(
        self,
        interaction: ModalInteraction
    ) -> ModalState:
        ...
