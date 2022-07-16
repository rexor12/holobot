from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar

from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable

TInteractable = TypeVar("TInteractable", bound=Interactable)

@dataclass
class InteractionDescriptor(Generic[TInteractable]):
    workflow: Optional[IWorkflow]
    interactable: Optional[TInteractable]
    arguments: Dict[str, Any] = field(default_factory=dict)
