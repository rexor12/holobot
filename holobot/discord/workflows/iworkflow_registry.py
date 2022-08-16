from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from typing import TypeVar

from hikari.api.special_endpoints import ContextMenuCommandBuilder, SlashCommandBuilder

from holobot.discord.bot import Bot
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Command, Component, Interactable, MenuItem

TInteractable = TypeVar("TInteractable", bound=Interactable)

class IWorkflowRegistry(metaclass=ABCMeta):
    """Interface for a service that keeps track of the available workflows."""

    @abstractmethod
    def get_command(
        self,
        group_name: str | None,
        subgroup_name: str | None,
        name: str
    ) -> tuple[IWorkflow, Command] | None:
        ...

    @abstractmethod
    def get_component(
        self,
        identifier: str
    ) -> tuple[IWorkflow, Component] | None:
        ...

    @abstractmethod
    def get_menu_item(
        self,
        name: str
    ) ->tuple[IWorkflow, MenuItem] | None:
        ...

    @abstractmethod
    def get_command_builders(self, bot: Bot) -> dict[str, Sequence[SlashCommandBuilder]]:
        """Gets the command builders for each server's commands.

        An empty string should be used as the key for global commands;
        otherwise, the server's identifier.

        :param bot: The current bot instance.
        :type bot: Bot
        :return: A list of command builders for each server.
        :rtype: dict[str, Sequence[SlashCommandBuilder]]
        """

    @abstractmethod
    def get_menu_item_builders(self, bot: Bot) -> dict[str, Sequence[ContextMenuCommandBuilder]]:
        """Gets the menu item builders for each server's menu items.

        An empty string should be used as the key for global menu items;
        otherwise, the server's identifier.

        :param bot: The current bot instance.
        :type bot: Bot
        :return: A list of menu item builders for each server.
        :rtype: dict[str, Sequence[ContextMenuCommandBuilder]]
        """
