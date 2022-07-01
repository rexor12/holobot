from .icomponent_interaction_processor import IComponentInteractionProcessor
from .icomponent_registry import IComponentRegistry
from .icomponent_transformer import IComponentTransformer
from ..actions.iaction_processor import IActionProcessor
from hikari import ComponentInteraction
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.commands.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, Dict, NamedTuple
from uuid import uuid4

import hikari
import time

class ComponentDetails(NamedTuple):
    component_id: str
    state: Dict[str, Any]

@injectable(IComponentInteractionProcessor)
class ComponentInteractionProcessor(IComponentInteractionProcessor):
    def __init__(
        self,
        action_processor: IActionProcessor,
        component_registry: IComponentRegistry,
        component_transformer: IComponentTransformer,
        log: LogInterface
    ) -> None:
        super().__init__()
        self.__action_processor: IActionProcessor = action_processor
        self.__log: LogInterface = log.with_name("Discord", "ComponentInteractionProcessor")
        self.__component_registry: IComponentRegistry = component_registry
        self.__component_transformer: IComponentTransformer = component_transformer

    async def process(self, interaction: ComponentInteraction) -> None:
        component_id = interaction.custom_id.split("~", 1)[0]
        self.__log.trace(f"Processing component interaction... {{ Id = {component_id}, UserId = {interaction.user.id} }}")
        if not (registration := self.__component_registry.get_registration(component_id)):
            await self.__action_processor.process(interaction, ReplyAction(content="You've invoked an inexistent command."), DeferType.NONE)
            self.__log.trace(f"Processed component interaction. {{ Id = {component_id}, IsInvalid = True }}")
            return

        start_time = time.perf_counter()
        if registration.deferral == DeferType.DEFER_MESSAGE_CREATION:
            await interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        elif registration.deferral == DeferType.DEFER_MESSAGE_UPDATE:
            await interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)

        context = await ComponentInteractionProcessor.__get_context(interaction)
        response = await registration.on_interaction(
            registration,
            context,
            self.__component_transformer.transform_state(registration.component_type, interaction))
        await self.__action_processor.process(interaction, response.action, registration.deferral)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.trace(f"Processed component interaction. {{ Id = {component_id}, UserId = {context.author_id}, Elapsed = {elapsed_time} }}")

    @staticmethod
    async def __get_context(interaction: ComponentInteraction) -> ServerChatInteractionContext:
        if not interaction.guild_id:
            raise NotImplementedError("Non-server specific commands are not supported.")

        return ServerChatInteractionContext(
            request_id=uuid4(),
            author_id=str(interaction.user.id),
            author_name=interaction.user.username,
            author_nickname=interaction.member.nickname if interaction.member else None,
            server_id=str(interaction.guild_id),
            server_name=await ComponentInteractionProcessor.__get_server_name(interaction),
            channel_id=str(interaction.channel_id)
        )

    @staticmethod
    async def __get_server_name(interaction: ComponentInteraction) -> str:
        server = interaction.get_guild()
        if server:
            return server.name
        server = await interaction.fetch_guild()
        return server.name if server else "Unknown"
