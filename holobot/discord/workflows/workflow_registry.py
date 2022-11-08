from collections.abc import Sequence

from hikari import CommandType
from hikari.api.special_endpoints import ContextMenuCommandBuilder, SlashCommandBuilder

from holobot.discord.bot import Bot
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Autocomplete, Command, Component, MenuItem
from holobot.discord.sdk.workflows.interactables.enums import MenuType
from holobot.discord.workflows.builders import (
    CommandBuilder, CommandGroupBuilder, CommandSubGroupBuilder
)
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import get_or_add
from .iworkflow_registry import IWorkflowRegistry

# key: command name
TCommandGroup = dict[str, tuple[IWorkflow, Command]]
TSubGroup = dict[str, TCommandGroup]
TGroup = dict[str, TSubGroup]

# 1st key: command name, 2nd key: option name (or empty string)
TAutocompleteMap = dict[str, dict[str, tuple[IWorkflow, Autocomplete]]]
# key: command subgroup name
TAutocompleteSubgroupMap = dict[str, TAutocompleteMap]
# key: command group name
TAutocompleteGroupMap = dict[str, TAutocompleteSubgroupMap]

@injectable(IWorkflowRegistry)
class WorkflowRegistry(IWorkflowRegistry):
    def __init__(
        self,
        debugger: DebuggerInterface,
        logger_factory: ILoggerFactory,
        workflows: tuple[IWorkflow, ...]
    ) -> None:
        super().__init__()
        self.__log = logger_factory.create(WorkflowRegistry)
        self.__initialize_groups(workflows, debugger)

    def get_command(
        self,
        group_name: str | None,
        subgroup_name: str | None,
        name: str
    ) -> tuple[IWorkflow, Command] | None:
        if (not (group := self.__commands.get(group_name or ""))
            or not (sub_group := group.get(subgroup_name or ""))
            or not (command := sub_group.get(name))):
            return None
        return command

    def get_component(
        self,
        identifier: str
    ) -> tuple[IWorkflow, Component] | None:
        return self.__components.get(identifier)

    def get_menu_item(
        self,
        name: str
    ) -> tuple[IWorkflow, MenuItem] | None:
        return self.__menu_items.get(name)

    def get_autocomplete(
        self,
        group_name: str | None,
        subgroup_name: str | None,
        command_name: str,
        option_name: str
    ) -> tuple[IWorkflow, Autocomplete] | None:
        if (not (group := self.__autocompletes.get(group_name or ""))
            or not (sub_group := group.get(subgroup_name or ""))
            or not (options := sub_group.get(command_name))):
            return None

        if option_name in options:
            return options[option_name]

        return options[""] if "" in options else None

    def get_command_builders(self, bot: Bot) -> dict[str, Sequence[SlashCommandBuilder]]:
        self.__log.info("Registering commands...")
        builders_by_servers: dict[str, dict[str, CommandGroupBuilder | CommandBuilder]] = {}
        subgroup_builders_by_servers: dict[str, dict[str, CommandSubGroupBuilder]] = {}
        total_command_count = 0
        for group_name, group in self.__commands.items():
            for subgroup_name, subgroup in group.items():
                for command_name, command in subgroup.items():
                    total_command_count += 1
                    for server_id in command[1].server_ids or ("",):
                        builders_by_server = get_or_add(builders_by_servers, server_id, lambda _: dict[str, CommandGroupBuilder | CommandBuilder](), None)
                        subgroup_builders_by_server = get_or_add(subgroup_builders_by_servers, server_id, lambda _: dict[str, CommandSubGroupBuilder](), None)
                        group_builder = None
                        subgroup_builder = None
                        if group_name:
                            group_builder = get_or_add(
                                builders_by_server,
                                group_name,
                                lambda state: CommandGroupBuilder(state, state, bot.rest.slash_command_builder),
                                group_name
                            )
                            if subgroup_name and isinstance(group_builder, CommandGroupBuilder):
                                subgroup_builder = get_or_add(
                                    subgroup_builders_by_server,
                                    subgroup_name,
                                    lambda state: state[0].with_sub_group(state[1], state[1]),
                                    (group_builder, subgroup_name)
                                )

                        if subgroup_builder:
                            WorkflowRegistry.__add_child_command(subgroup_builder, command[1], command_name)
                        elif isinstance(group_builder, CommandGroupBuilder):
                            WorkflowRegistry.__add_child_command(group_builder, command[1], command_name)
                        else:
                            builders_by_server[command_name] = WorkflowRegistry.__create_command(bot, command[1], command_name)

        self.__log.info("Successfully registered commands", count=total_command_count)
        return {
            server_id: [builder.build() for builder in builders.values()]
            for server_id, builders in builders_by_servers.items()
        }

    def get_menu_item_builders(self, bot: Bot) -> dict[str, Sequence[ContextMenuCommandBuilder]]:
        self.__log.info("Registering user menu items...")
        builders = {}
        for menu_item in sorted(self.__menu_items.values(), key=lambda i: i[1].priority, reverse=True):
            for server_id in menu_item[1].server_ids or ("",):
                server_builders = get_or_add(builders, server_id, lambda _: list(), None)
                if (server_builders := builders.get(server_id)) is None:
                    builders[server_id] = server_builders = []
                server_builders.append(self.__get_user_menu_item_builder(bot, menu_item[1]))
        self.__log.info("Successfully registered user menu items", count=len(self.__menu_items))
        return builders

    @staticmethod
    def __create_command(
        bot: Bot,
        command: Command,
        command_name: str
    ) -> CommandBuilder:
        builder = CommandBuilder(command_name, command.description or command.name, bot.rest.slash_command_builder)
        for option in command.options:
            builder.with_option(option)
        return builder

    @staticmethod
    def __add_child_command(
        sub_group_builder: CommandGroupBuilder | CommandSubGroupBuilder,
        command: Command,
        command_name: str
    ) -> None:
        builder = sub_group_builder.with_command(command_name, command.description or command.name)
        for option in command.options:
            builder.with_option(option)

    @staticmethod
    def __add_command(
        command_groups: TGroup,
        workflow: IWorkflow,
        command: Command,
        debugger: DebuggerInterface
    ) -> None:
        group_name = command.group_name or ""
        subgroup_name = command.subgroup_name or ""

        if group_name not in command_groups:
            command_groups[group_name] = command_subgroups = {}
        else:
            command_subgroups = command_groups[group_name]

        if subgroup_name not in command_subgroups:
            command_subgroups[subgroup_name] = commands = {}
        else:
            commands = command_subgroups[subgroup_name]

        command_name = f"d{command.name}" if debugger.is_debug_mode_enabled() else command.name
        commands[command_name] = (workflow, command)

    @staticmethod
    def __add_autocomplete(
        autocomplete_groups: TAutocompleteGroupMap,
        workflow: IWorkflow,
        autocomplete: Autocomplete,
        debugger: DebuggerInterface
    ) -> None:
        group_name = autocomplete.group_name or ""
        subgroup_name = autocomplete.subgroup_name or ""

        if group_name not in autocomplete_groups:
            autocomplete_groups[group_name] = autocomplete_subgroups = {}
        else:
            autocomplete_subgroups = autocomplete_groups[group_name]

        if subgroup_name not in autocomplete_subgroups:
            autocomplete_subgroups[subgroup_name] = autocomplete_options = {}
        else:
            autocomplete_options = autocomplete_subgroups[subgroup_name]

        for option_name in (autocomplete.options or ("")):
            autocomplete_name = (
                f"d{autocomplete.name}"
                if debugger.is_debug_mode_enabled()
                else autocomplete.name
            )
            if autocomplete_name not in autocomplete_options:
                autocomplete_options[autocomplete_name] = autocomplete_option = {}
            else:
                autocomplete_option = autocomplete_options[autocomplete_name]

            autocomplete_option[option_name] = (workflow, autocomplete)

    def __initialize_groups(
        self,
        workflows: tuple[IWorkflow, ...],
        debugger: DebuggerInterface
    ) -> None:
        commands: TGroup = {}
        components: dict[str, tuple[IWorkflow, Component]] = {}
        menu_items: dict[str, tuple[IWorkflow, MenuItem]] = {}
        autocompletes: TAutocompleteGroupMap = {}
        for workflow in workflows:
            for interactable in workflow.interactables:
                match interactable:
                    case Command(): WorkflowRegistry.__add_command(commands, workflow, interactable, debugger)
                    case Component(): components[interactable.identifier] = (workflow, interactable)
                    case MenuItem(): menu_items[interactable.title] = (workflow, interactable)
                    case Autocomplete(): WorkflowRegistry.__add_autocomplete(autocompletes, workflow, interactable, debugger)
                    case _: self.__log.warning("Ignored unknown interactable type", type=type(interactable).__name__)
        self.__commands = commands
        self.__components = components
        self.__menu_items = menu_items
        self.__autocompletes = autocompletes

    def __get_user_menu_item_builder(
        self,
        bot: Bot,
        menu_item: MenuItem
    ) -> ContextMenuCommandBuilder:
        builder = bot.rest.context_menu_command_builder(
            type=CommandType.USER if menu_item.menu_type is MenuType.USER else CommandType.MESSAGE,
            name=menu_item.title
        )
        self.__log.debug("Registered menu item", name=menu_item.title, type=menu_item.menu_type.value)
        return builder
