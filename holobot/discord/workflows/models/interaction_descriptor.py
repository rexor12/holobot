from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable

TInteractable = TypeVar("TInteractable", bound=Interactable)

@dataclass(kw_only=True)
class InteractionDescriptor(Generic[TInteractable]):
    workflow: IWorkflow | None
    interactable: TInteractable | None
    arguments: dict[str, Any] = field(default_factory=dict)

    initiator_id: int
    """The identifier of the user who initiated this interaction."""

    bound_user_id: int
    """The identifier of the user who initiated the workflow."""

    context: InteractionContext
    """Contextual information about the interaction."""
