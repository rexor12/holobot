from .icommand_processor import ICommandProcessor
from .icommand_registry import ICommandRegistry
from ..actions import IActionProcessor
from hikari import CommandInteraction, OptionType, ResponseType
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.commands import CommandExecutionRuleInterface, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.events import CommandExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Any, Dict, NamedTuple, Optional, Tuple
from uuid import uuid4

import time

class CommandDetails(NamedTuple):
    group_name: Optional[str]
    sub_group_name: Optional[str]
    command_name: str
    arguments: Dict[str, Any]

@injectable(ICommandProcessor)
class CommandProcessor(ICommandProcessor):
    def __init__(self,
        action_processor: IActionProcessor,
        log: LogInterface,
        command_executed_event_handlers: Tuple[ListenerInterface[CommandExecutedEvent], ...],
        command_execution_rules: Tuple[CommandExecutionRuleInterface, ...],
        command_registry: ICommandRegistry) -> None:
        super().__init__()
        self.__action_processor: IActionProcessor = action_processor
        self.__log: LogInterface = log.with_name("Discord", "CommandProcessor")
        self.__command_executed_event_handlers: Tuple[ListenerInterface[CommandExecutedEvent], ...] = command_executed_event_handlers
        self.__command_execution_rules: Tuple[CommandExecutionRuleInterface, ...] = command_execution_rules
        self.__command_registry: ICommandRegistry = command_registry

    async def process(self, interaction: CommandInteraction) -> None:
        details = CommandProcessor.__get_command_details(interaction)
        self.__log.trace(f"Processing command... {{ Name = {details.command_name} }}")
        start_time = time.perf_counter()
        await interaction.create_initial_response(response_type=ResponseType.DEFERRED_MESSAGE_CREATE)

        context = await CommandProcessor.__get_context(interaction)
        if not (command := self.__command_registry.get_command(details.group_name, details.sub_group_name, details.command_name)):
            await self.__action_processor.process(interaction, ReplyAction(content="You've invoked an inexistent command."), DeferType.DEFER_MESSAGE_CREATION)
            return

        for rule in self.__command_execution_rules:
            if await rule.should_halt(command, context):
                self.__log.debug(f"Command has been halted. {{ Name = {command.name}, Group = {command.group_name}, SubGroup = {command.subgroup_name}, UserId = {context.author_id}, Rule = {type(rule).__name__} }}")
                await self.__action_processor.process(interaction, ReplyAction(content="You're not allowed to use this command here."), DeferType.DEFER_MESSAGE_CREATION)
                return

        # TODO Is this **kwargs expansion safe? Maybe bind known params only?
        response = await command.execute(context, **details.arguments)
        await self.__action_processor.process(interaction, response.action, DeferType.DEFER_MESSAGE_CREATION)
        await self.__on_command_executed(command, interaction, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Processed command. {{ Name = {interaction.command_name}, Elapsed = {elapsed_time} }}")

    @staticmethod
    async def __get_context(interaction: CommandInteraction) -> ServerChatInteractionContext:
        if not interaction.guild_id:
            raise NotImplementedError("Non-server specific commands are not supported.")

        return ServerChatInteractionContext(
            request_id=uuid4(),
            author_id=str(interaction.user.id),
            author_name=interaction.user.username,
            author_nickname=interaction.member.nickname if interaction.member else None,
            server_id=str(interaction.guild_id),
            server_name=await CommandProcessor.__get_server_name(interaction),
            channel_id=str(interaction.channel_id)
        )

    @staticmethod
    async def __get_server_name(interaction: CommandInteraction) -> str:
        server = interaction.get_guild()
        if server:
            return server.name
        server = await interaction.fetch_guild()
        return server.name if server else "Unknown"

    @staticmethod
    def __get_command_details(interaction: CommandInteraction) -> CommandDetails:
        group_name = None
        sub_group_name = None
        command_name = interaction.command_name
        arguments = {}
        options = list(interaction.options) if interaction.options else []
        while options:
            option = options.pop(0)
            if option.type == OptionType.SUB_COMMAND_GROUP:
                group_name = interaction.command_name
                sub_group_name = option.name
                options = list(option.options) if option.options else []
            elif option.type == OptionType.SUB_COMMAND:
                group_name = group_name or interaction.command_name
                command_name = option.name
                options = list(option.options) if option.options else []
            else: arguments[option.name] = option.value

        return CommandDetails(
            group_name,
            sub_group_name,
            command_name,
            arguments
        )

    async def __on_command_executed(self, command: CommandInterface, interaction: CommandInteraction, response: CommandResponse) -> None:
        event = CommandExecutedEvent(
            command_type=type(command),
            server_id=str(interaction.guild_id),
            user_id=str(interaction.user.id),
            command=command.name,
            group=command.group_name,
            subgroup=command.subgroup_name,
            response=response
        )
        for handler in self.__command_executed_event_handlers:
            await handler.on_event(event)
