from collections.abc import Sequence
from ctypes import ArgumentError
from dataclasses import dataclass, field
from itertools import islice
from typing import TypeVar

from holobot.discord.sdk.workflows.interactables.components import ComponentStateBase
from holobot.sdk.utils.iterable_utils import first
from .embed import Embed

TComponent = TypeVar("TComponent", bound=ComponentStateBase)

@dataclass(kw_only=True, frozen=True)
class Message:
    author_id: int
    server_id: int | None
    channel_id: int
    message_id: int
    content: str | None = None
    embeds: Sequence[Embed] = field(default_factory=tuple)
    components: Sequence[ComponentStateBase] = field(default_factory=tuple)

    def get_component(
        self,
        identifier: str,
        index: int = 0
    ) -> ComponentStateBase:
        filtered_components = filter(
            lambda component: component.identifier == identifier,
            self.components
        )

        return first(islice(filtered_components, index, index + 1))

    def get_typed_component(
        self,
        component_type: type[TComponent],
        identifier: str,
        index: int = 0
    ) -> TComponent:
        component = self.get_component(identifier, index)
        if not isinstance(component, component_type):
            raise ArgumentError(
                "component_type",
                f"The component with the identifier '{identifier}' is not of type '{component_type}'."
            )

        return component
