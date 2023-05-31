from collections.abc import Sequence
from typing import Protocol, TypeVar

from hikari.api.special_endpoints import (
    CommandBuilder, ContextMenuCommandBuilder, SlashCommandBuilder
)

from holobot.discord.bot import Bot
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import (
    Autocomplete, Command, Component, Interactable, MenuItem, Modal
)

TInteractable = TypeVar("TInteractable", bound=Interactable)

class IWorkflowRegistry(Protocol):
    """Interface for a service that keeps track of the available workflows."""

    def get_command(
        self,
        group_name: str | None,
        subgroup_name: str | None,
        name: str
    ) -> tuple[IWorkflow, Command] | None:
        ...

    def get_component(
        self,
        identifier: str
    ) -> tuple[IWorkflow, Component] | None:
        ...

    def get_menu_item(
        self,
        name: str
    ) ->tuple[IWorkflow, MenuItem] | None:
        ...

    def get_autocomplete(
        self,
        group_name: str | None,
        subgroup_name: str | None,
        command_name: str,
        option_name: str
    ) -> tuple[IWorkflow, Autocomplete] | None:
        """Gets the autocomplete interactable for the specified command and option.

        If there is no autocomplete interactable for the specified option,
        then the one suitable for every option is returned, if exists.

        :param group_name: The name of the command's group.
        :type group_name: str | None
        :param subgroup_name: The name of the command's subgroup.
        :type subgroup_name: str | None
        :param command_name: The name of the command.
        :type command_name: str
        :param option_name: The name of the option.
        :type option_name: str
        :return: If exists, a suitable autocomplete interactable.
        :rtype: tuple[IWorkflow, Autocomplete] | None
        """
        ...

    def get_modal(
        self,
        identifier: str
    ) -> tuple[IWorkflow, Modal] | None:
        """Gets the modal interactable with the specified identifier.

        :param identifier: The identifier of the modal.
        :type identifier: str
        :return: If exists, the modal interactable.
        :rtype: tuple[IWorkflow, Modal] | None
        """
        ...

    def get_command_builders(self, bot: Bot) -> dict[str, Sequence[SlashCommandBuilder]]:
        """Gets the command builders for each server's commands.

        An empty string should be used as the key for global commands;
        otherwise, the server's identifier.

        :param bot: The current bot instance.
        :type bot: Bot
        :return: A list of command builders for each server.
        :rtype: dict[str, Sequence[SlashCommandBuilder]]
        """
        ...

    def get_menu_item_builders(self, bot: Bot) -> dict[str, Sequence[ContextMenuCommandBuilder]]:
        """Gets the menu item builders for each server's menu items.

        An empty string should be used as the key for global menu items;
        otherwise, the server's identifier.

        :param bot: The current bot instance.
        :type bot: Bot
        :return: A list of menu item builders for each server.
        :rtype: dict[str, Sequence[ContextMenuCommandBuilder]]
        """
        ...
