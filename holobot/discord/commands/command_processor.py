from .icommand_processor import ICommandProcessor
from ..actions import IActionProcessor
from ..contexts import IContextManager
from discord_slash import SlashContext
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandExecutionRuleInterface, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.events import CommandExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Any, Tuple
from uuid import uuid4

import time

@injectable(ICommandProcessor)
class CommandProcessor(ICommandProcessor):
    def __init__(self,
        action_processor: IActionProcessor,
        log: LogInterface,
        command_executed_event_handlers: Tuple[ListenerInterface[CommandExecutedEvent], ...],
        command_execution_rules: Tuple[CommandExecutionRuleInterface, ...],
        context_manager: IContextManager) -> None:
        super().__init__()
        self.__action_processor: IActionProcessor = action_processor
        self.__log: LogInterface = log.with_name("Discord", "CommandProcessor")
        self.__command_executed_event_handlers: Tuple[ListenerInterface[CommandExecutedEvent], ...] = command_executed_event_handlers
        self.__command_execution_rules: Tuple[CommandExecutionRuleInterface, ...] = command_execution_rules
        self.__context_manager: IContextManager = context_manager

    async def process(self, __command: CommandInterface, context: SlashContext, **kwargs: Any) -> None:
        # TODO Strip str type kwargs.
        self.__log.trace(f"Processing command... {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id} }}")
        start_time = time.perf_counter()
        await context.defer()
        interaction_context = CommandProcessor.__transform_context(context)

        async with await self.__context_manager.register_context(interaction_context.request_id, context):
            for rule in self.__command_execution_rules:
                if await rule.should_halt(__command, interaction_context):
                    self.__log.debug(f"Command has been halted. {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id} }}")
                    await self.__action_processor.process(context, ReplyAction(content="You're not allowed to use this command here."))
                    return

            response = await __command.execute(interaction_context, **kwargs)
            await self.__action_processor.process(context, response.action)
            await self.__on_command_executed(__command, context, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Processed command. {{ Name = {__command.name}, Group = {__command.group_name}, SubGroup = {__command.subgroup_name}, UserId = {context.author_id}, Elapsed = {elapsed_time} }}")

    @staticmethod
    def __transform_context(context: SlashContext) -> ServerChatInteractionContext:
        return ServerChatInteractionContext(
            request_id=uuid4(),
            author_id=str(context.author_id),
            author_name=context.author.name,
            author_nickname=context.author.nick,
            server_id=str(context.guild_id),
            channel_id=str(context.channel_id)
        )

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
