from typing import Protocol

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import Embed
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, Layout
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from .constants import WORKFLOW_PREDEFINED_INTERACTABLES
from .interactables import Interactable
from .iworkflow import IWorkflow
from .workflow_meta import WorkflowMeta

class MixinMeta(WorkflowMeta, type(Protocol)):
    pass

class WorkflowBase(IWorkflow, metaclass=MixinMeta):
    @property
    def name(self) -> str:
        return self.__name

    @property
    def required_permissions(self) -> Permission:
        return self.__required_permissions

    @property
    def interactables(self) -> tuple[Interactable, ...]:
        return tuple(self.__interactables)

    def __init__(
        self,
        *,
        name: str | None = None,
        interactables: tuple[Interactable, ...] = (),
        required_permissions: Permission = Permission.NONE
    ) -> None:
        self.__name: str = name or type(self).__name__
        self.__required_permissions: Permission = required_permissions
        predefined_interactables: list[Interactable] = getattr(
            self,
            WORKFLOW_PREDEFINED_INTERACTABLES,
            []
        )
        self.__interactables: list[Interactable] = list(predefined_interactables)
        self.__interactables.extend(interactables)

    def __str__(self) -> str:
        return type(self).__name__

    def add_registration(self, registration: Interactable) -> None:
        self.__interactables.append(registration)

    def _reply(
        self,
        *,
        content: str | Embed,
        components: ComponentBase | list[Layout] | None = None,
        suppress_user_mentions: bool = False
    ) -> InteractionResponse:
        return InteractionResponse(
            action=ReplyAction(
                content=content,
                components=components or [],
                suppress_user_mentions=suppress_user_mentions
            )
        )
