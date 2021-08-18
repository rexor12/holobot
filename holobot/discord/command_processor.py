from .icommand_processor import ICommandProcessor
from discord_slash import SlashContext
from holobot.discord.sdk.commands import CommandExecutionRuleInterface, CommandInterface, CommandResponse
from holobot.discord.sdk.events import CommandExecutedEvent
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Any, Tuple

import time

@injectable(ICommandProcessor)
class CommandProcessor(ICommandProcessor):
    def __init__(self,
        log: LogInterface,
        command_executed_event_handlers: Tuple[ListenerInterface[CommandExecutedEvent], ...],
        command_execution_rules: Tuple[CommandExecutionRuleInterface, ...]) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "CommandProcessor")
        self.__command_executed_event_handlers: Tuple[ListenerInterface[CommandExecutedEvent], ...] = command_executed_event_handlers
        self.__command_execution_rules: Tuple[CommandExecutionRuleInterface, ...] = command_execution_rules

    async def process(self, __command: CommandInterface, context: SlashContext, **kwargs: Any) -> None:
        self.__log.trace(f"Executing command... {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id} }}")
        start_time = time.perf_counter()
        await context.defer()
        for rule in self.__command_execution_rules:
            if await rule.should_halt(__command, context):
                self.__log.debug(f"Command has been halted. {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id} }}")
                await reply(context, "You're not allowed to use this command here.")
                return

        response = await __command.execute(context, **kwargs)
        await self.__on_command_executed(__command, context, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Executed command. {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id}, Elapsed = {elapsed_time} }}")

    async def __on_command_executed(self, command: CommandInterface, context: SlashContext, response: CommandResponse) -> None:
        event = CommandExecutedEvent(
            command_type=type(command),
            server_id=str(context.guild_id),
            user_id=str(context.author_id),
            command=command.name,
            group=command.group_name,
            subgroup=command.subgroup_name,
            response=response
        )
        for handler in self.__command_executed_event_handlers:
            await handler.on_event(event)
