from dataclasses import dataclass

from holobot.discord.sdk.workflows.interactables.components import ComponentStateBase
from .interactable import Interactable

@dataclass(kw_only=True)
class Component(Interactable):
    identifier: str
    """The globally unique identifier of the component.

    The same identifier CANNOT be used by multiple components to avoid ambiguity.
    """

    state_type: type[ComponentStateBase]
    """The type of the component's state.

    This overrides the default behavior in cases where complex states are supported.
    """

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.identifier})"
