from collections.abc import Sequence
from typing import NamedTuple, Protocol

import hikari
import hikari.api.special_endpoints as special_endpoints
import hikari.impl.special_endpoints as endpoints

from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, ComponentStateBase, LayoutBase
)
from holobot.discord.sdk.workflows.interactables.views import Modal, ModalState

class ComponentId(NamedTuple):
    identifier: str
    index: int

class IComponentTransformer(Protocol):
    def create_controls(
        self,
        controls: ComponentBase | Sequence[LayoutBase]
    ) -> list[special_endpoints.ComponentBuilder]:
        ...

    def create_modal(
        self,
        view: Modal
    ) -> list[special_endpoints.ModalActionRowBuilder]:
        ...

    def create_modal_state(
        self,
        interaction: hikari.ModalInteraction
    ) -> ModalState:
        ...

    def create_control_states(
        self,
        interaction: hikari.ComponentInteraction,
        expected_target_types: dict[str, type[ComponentStateBase]]
    ) -> Sequence[ComponentStateBase]:
        ...

    def get_component_id(self, custom_id: str) -> ComponentId:
        ...
