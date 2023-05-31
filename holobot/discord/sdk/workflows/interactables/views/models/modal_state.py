from dataclasses import dataclass, field
from typing import TypeVar

from holobot.discord.sdk.workflows.interactables.components.models import ComponentStateBase
from holobot.sdk.exceptions import ArgumentError
from .view_state_base import ViewStateBase

T = TypeVar("T", bound=ComponentStateBase)

@dataclass(kw_only=True)
class ModalState(ViewStateBase):
    """Represents the state of a modal."""

    components: dict[str, ComponentStateBase] = field(default_factory=dict)
    """The states of the components that belong to this modal."""

    def get_component_state(
        self,
        state_type: type[T],
        identifier: str
    ) -> T:
        if (state := self.components.get(identifier)) is None:
            raise ArgumentError(
                "identifier",
                f"The component state with the identifier '{identifier}' cannot be found."
            )

        if not isinstance(state, state_type):
            raise ArgumentError(
                "state_type",
                f"The component state with the identifier '{identifier}'"
                f" is of type '{type(state)}' instead of type '{state_type}'."
            )

        return state

    def try_get_component_state(
        self,
        state_type: type[T],
        identifier: str
    ) -> T | None:
        if (state := self.components.get(identifier)) is None:
            return None

        if not isinstance(state, state_type):
            return None

        return state

    def has_component_state(
        self,
        state_type: type[T],
        identifier: str
    ) -> bool:
        if (state := self.components.get(identifier)) is None:
            return False

        if not isinstance(state, state_type):
            return False

        return True
