from .icommand_registry import ICommandRegistry
from .builders import CommandBuilder, CommandGroupBuilder, CommandSubGroupBuilder
from ..bot import Bot
from hikari.api.special_endpoints import SlashCommandBuilder
from holobot.discord.sdk.commands import CommandInterface
from holobot.sdk.diagnostics import DebuggerInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Dict, Optional, Sequence, Tuple, Union

TCommandGroup = Dict[str, CommandInterface]
TSubGroup = Dict[str, TCommandGroup]
TGroup = Dict[str, TSubGroup]

@injectable(ICommandRegistry)
class CommandRegistry(ICommandRegistry):
    def __init__(
        self,
        commands: Tuple[CommandInterface, ...],
        debugger: DebuggerInterface,
        log: LogInterface
    ) -> None:
        super().__init__()
        self.__commands: TGroup = CommandRegistry.__initialize_command_groups(commands, debugger)
        self.__log: LogInterface = log.with_name("Discord", "CommandRegistry")

    def get_command(
        self,
        group_name: Optional[str],
        sub_group_name: Optional[str],
        name: str
    ) -> Optional[CommandInterface]:
        if (not (group := self.__commands.get(group_name or ""))
            or not (sub_group := group.get(sub_group_name or ""))
            or not (command := sub_group.get(name))):
            return None
        return command

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
                        CommandRegistry.__add_child_command(subgroup_builder, command, command_name)
                    elif group_builder:
                        CommandRegistry.__add_child_command(group_builder, command, command_name)
                    else:
                        builders.append(CommandRegistry.__create_command(bot, command, command_name))
                    total_command_count = total_command_count + 1
                    self.__log.debug(f"Registered command. {{ Group = {command.group_name}, SubGroup = {command.subgroup_name}, Name = {command_name} }}")
            if group_builder:
                builders.append(group_builder.build())
        self.__log.info(f"Successfully registered commands. {{ Count = {total_command_count} }}")
        return builders

    @staticmethod
    def __initialize_command_groups(
        application_commands: Sequence[CommandInterface],
        debugger: DebuggerInterface
    ) -> TGroup:
        command_groups: TGroup = {}
        for command in application_commands:
            group_name = command.group_name or ""
            subgroup_name = command.subgroup_name or ""

            if group_name not in command_groups:
                command_groups[group_name] = command_subgroups = {}
            else: command_subgroups = command_groups[group_name]

            if subgroup_name not in command_subgroups:
                command_subgroups[subgroup_name] = commands = {}
            else: commands = command_subgroups[subgroup_name]

            command_name = f"d{command.name}" if debugger.is_debug_mode_enabled() else command.name
            commands[command_name] = command

        return command_groups

    @staticmethod
    def __create_command(
        bot: Bot,
        command: CommandInterface,
        command_name: str
    ) -> SlashCommandBuilder:
        builder = CommandBuilder(command_name, command.description or command.name, bot.rest.slash_command_builder)
        for option in command.options:
            builder.with_option(option)
        return builder.build()

    @staticmethod
    def __add_child_command(
        sub_group_builder: Union[CommandGroupBuilder, CommandSubGroupBuilder],
        command: CommandInterface,
        command_name: str
    ) -> None:
        builder = sub_group_builder.with_command(command_name, command.description or command.name)
        for option in command.options:
            builder.with_option(option)
