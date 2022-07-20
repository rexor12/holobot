from abc import ABCMeta, abstractmethod
from typing import Optional, Sequence, Tuple, TypeVar

from hikari.api.special_endpoints import ContextMenuCommandBuilder, SlashCommandBuilder

from holobot.discord.bot import Bot
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Command, Component, Interactable, MenuItem

TInteractable = TypeVar("TInteractable", bound=Interactable)

class IWorkflowRegistry(metaclass=ABCMeta):
    @abstractmethod
    def get_command(
        self,
        group_name: Optional[str],
        subgroup_name: Optional[str],
        name: str
    ) -> Optional[Tuple[IWorkflow, Command]]:
        ...

    @abstractmethod
    def get_component(
        self,
        identifier: str
    ) -> Optional[Tuple[IWorkflow, Component]]:
        ...

    @abstractmethod
    def get_menu_item(
        self,
        name: str
    ) -> Optional[Tuple[IWorkflow, MenuItem]]:
        ...

    @abstractmethod
    def get_command_builders(self, bot: Bot) -> Sequence[SlashCommandBuilder]:
        ...

    @abstractmethod
    def get_menu_item_builders(self, bot: Bot) -> Sequence[ContextMenuCommandBuilder]:
        ...
