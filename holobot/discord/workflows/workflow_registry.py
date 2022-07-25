from typing import Dict, Optional, Sequence, Tuple, Union

from hikari import CommandType
from hikari.api.special_endpoints import ContextMenuCommandBuilder, SlashCommandBuilder

from .iworkflow_registry import IWorkflowRegistry
from holobot.discord.bot import Bot
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Command, Component, MenuItem
from holobot.discord.sdk.workflows.interactables.enums import MenuType
from holobot.discord.workflows.builders import CommandBuilder, CommandGroupBuilder, CommandSubGroupBuilder
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

TCommandGroup = Dict[str, Tuple[IWorkflow, Command]]
TSubGroup = Dict[str, TCommandGroup]
TGroup = Dict[str, TSubGroup]

@injectable(IWorkflowRegistry)
class WorkflowRegistry(IWorkflowRegistry):
    def __init__(
        self,
        debugger: DebuggerInterface,
        logger_factory: ILoggerFactory,
        workflows: Tuple[IWorkflow, ...]
    ) -> None:
        super().__init__()
        self.__log = logger_factory.create(WorkflowRegistry)
        self.__initialize_groups(workflows, debugger)

    def get_command(
        self,
        group_name: Optional[str],
        subgroup_name: Optional[str],
        name: str
    ) -> Optional[Tuple[IWorkflow, Command]]:
        if (not (group := self.__commands.get(group_name or ""))
            or not (sub_group := group.get(subgroup_name or ""))
            or not (command := sub_group.get(name))):
            return None
        return command

    def get_component(
        self,
        identifier: str
    ) -> Optional[Tuple[IWorkflow, Component]]:
        return self.__components.get(identifier)

    def get_menu_item(
        self,
        name: str
    ) -> Optional[Tuple[IWorkflow, MenuItem]]:
        return self.__menu_items.get(name)

    def get_command_builders(self, bot: Bot) -> Sequence[SlashCommandBuilder]:
        self.__log.info("Registering commands...")
        builders = []
        total_command_count = 0
        for group_name, group in self.__commands.items():
            group_builder = CommandGroupBuilder(group_name, group_name, bot.rest.slash_command_builder) if group_name else None
            for subgroup_name, subgroup in group.items():
                if subgroup_name and group_builder:
                    subgroup_builder = group_builder.with_sub_group(subgroup_name, subgroup_name)
                else: subgroup_builder = None

                for command_name, command in subgroup.items():
                    if subgroup_builder:
                        WorkflowRegistry.__add_child_command(subgroup_builder, command[1], command_name)
                    elif group_builder:
                        WorkflowRegistry.__add_child_command(group_builder, command[1], command_name)
                    else:
                        builders.append(WorkflowRegistry.__create_command(bot, command[1], command_name))
                    total_command_count = total_command_count + 1
                    self.__log.debug(f"Registered command. {{ Group = {command[1].group_name}, SubGroup = {command[1].subgroup_name}, Name = {command_name} }}")
            if group_builder:
                builders.append(group_builder.build())
        self.__log.info(f"Successfully registered commands. {{ Count = {total_command_count} }}")
        return builders

    def get_menu_item_builders(self, bot: Bot) -> Sequence[ContextMenuCommandBuilder]:
        self.__log.info("Registering user menu items...")
        context_menu_item_builders = []
        for menu_item in sorted(self.__menu_items.values(), key=lambda i: i[1].priority, reverse=True):
            if isinstance(menu_item[1], MenuItem):
                context_menu_item_builders.append(self.__get_user_menu_item_builder(bot, menu_item[1]))
            else: raise TypeError(f"Unexpected menu item type '{type(menu_item)}'.")
        self.__log.info(f"Successfully registered user menu items. {{ Count = {len(self.__menu_items)} }}")
        return context_menu_item_builders

    @staticmethod
    def __create_command(
        bot: Bot,
        command: Command,
        command_name: str
    ) -> SlashCommandBuilder:
        builder = CommandBuilder(command_name, command.description or command.name, bot.rest.slash_command_builder)
        for option in command.options:
            builder.with_option(option)
        return builder.build()

    @staticmethod
    def __add_child_command(
        sub_group_builder: Union[CommandGroupBuilder, CommandSubGroupBuilder],
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
        else: command_subgroups = command_groups[group_name]

        if subgroup_name not in command_subgroups:
            command_subgroups[subgroup_name] = commands = {}
        else: commands = command_subgroups[subgroup_name]

        command_name = f"d{command.name}" if debugger.is_debug_mode_enabled() else command.name
        commands[command_name] = (workflow, command)

    def __initialize_groups(
        self,
        workflows: Tuple[IWorkflow, ...],
        debugger: DebuggerInterface
    ) -> None:
        commands: TGroup = {}
        components: Dict[str, Tuple[IWorkflow, Component]] = {}
        menu_items: Dict[str, Tuple[IWorkflow, MenuItem]] = {}
        for workflow in workflows:
            for interactable in workflow.interactables:
                if isinstance(interactable, Command):
                    WorkflowRegistry.__add_command(commands, workflow, interactable, debugger)
                elif isinstance(interactable, Component):
                    components[interactable.identifier] = (workflow, interactable)
                elif isinstance(interactable, MenuItem):
                    menu_items[interactable.title] = (workflow, interactable)
        self.__commands = commands
        self.__components = components
        self.__menu_items = menu_items

    def __get_user_menu_item_builder(
        self,
        bot: Bot,
        menu_item: MenuItem
    ) -> ContextMenuCommandBuilder:
        builder = bot.rest.context_menu_command_builder(
            type=CommandType.USER if menu_item.menu_type == MenuType.USER else CommandType.MESSAGE,
            name=menu_item.title
        )
        self.__log.debug(f"Registered menu item. {{ Name = {menu_item.title}, Type = {menu_item.menu_type} }}")
        return builder
