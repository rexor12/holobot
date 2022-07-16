from typing import List, Tuple

from .constants import WORKFLOW_PREDEFINED_INTERACTABLES
from .interactables import Interactable
from .iworkflow import IWorkflow
from .workflow_meta import WorkflowMeta
from ..enums import Permission

class WorkflowBase(IWorkflow, metaclass=WorkflowMeta):
    @property
    def name(self) -> str:
        return self.__name

    @property
    def required_permissions(self) -> Permission:
        return self.__required_permissions

    @property
    def interactables(self) -> Tuple[Interactable, ...]:
        return tuple(self.__interactables)

    def __init__(
        self,
        name: str,
        *,
        interactables: Tuple[Interactable, ...] = (),
        required_permissions: Permission = Permission.NONE
    ) -> None:
        self.__name: str = name
        self.__required_permissions: Permission = required_permissions
        predefined_interactables: List[Interactable] = getattr(
            self,
            WORKFLOW_PREDEFINED_INTERACTABLES,
            []
        )
        self.__interactables: List[Interactable] = list(predefined_interactables)
        self.__interactables.extend(interactables)

    def add_registration(self, registration: Interactable) -> None:
        self.__interactables.append(registration)
