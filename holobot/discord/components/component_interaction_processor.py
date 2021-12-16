from .icomponent_interaction_processor import IComponentInteractionProcessor
from .icomponent_transformer import IComponentTransformer
from ..actions.iaction_processor import IActionProcessor
from ..contexts import IContextManager
from discord_slash.context import ComponentContext
from holobot.discord.sdk.commands.models import ServerChatInteractionContext
from holobot.discord.sdk.components.models import ComponentRegistration
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from uuid import uuid4

import time

@injectable(IComponentInteractionProcessor)
class ComponentInteractionProcessor(IComponentInteractionProcessor):
    def __init__(self,
                 action_processor: IActionProcessor,
                 component_transformer: IComponentTransformer,
                 context_manager: IContextManager,
                 log: LogInterface) -> None:
        super().__init__()
        self.__action_processor: IActionProcessor = action_processor
        self.__context_manager: IContextManager = context_manager
        self.__log: LogInterface = log.with_name("Discord", "ComponentInteractionProcessor")
        self.__component_transformer: IComponentTransformer = component_transformer

    async def process(self, registration: ComponentRegistration, context: ComponentContext) -> None:
        self.__log.trace(f"Processing component interaction... {{ Id = {registration.id}, UserId = {context.author_id} }}")
        start_time = time.perf_counter()
        await context.defer()
        interaction_context = ComponentInteractionProcessor.__transform_context(context)
        
        async with await self.__context_manager.register_context(interaction_context.request_id, context):
            response = await registration.on_interaction(
                registration,
                interaction_context,
                self.__component_transformer.transform_state(registration.component_type, context.data))
            await self.__action_processor.process(context, response.action)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.trace(f"Processed component interaction. {{ Id = {registration.id}, UserId = {context.author_id}, Elapsed = {elapsed_time} }}")

    @staticmethod
    def __transform_context(context: ComponentContext) -> ServerChatInteractionContext:
        if context.guild_id is None:
            raise NotImplementedError("Non-server specific commands are not supported.")

        return ServerChatInteractionContext(
            request_id=uuid4(),
            author_id=str(context.author_id),
            author_name=context.author.name, # type: ignore
            author_nickname=context.author.nick, # type: ignore
            server_id=str(context.guild_id),
            server_name=context.guild.name, # type: ignore
            channel_id=str(context.channel_id)
        )
