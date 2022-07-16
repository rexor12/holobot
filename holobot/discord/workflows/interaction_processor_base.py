from abc import ABCMeta, abstractmethod
from typing import Any, Coroutine, Dict, Generic, Optional, Tuple, TypeVar

import time

import hikari

from .iinteraction_processor import IInteractionProcessor, TInteraction
from .models import InteractionDescriptor
from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.sdk.logging import LogInterface

TInteractable = TypeVar("TInteractable", bound=Interactable, contravariant=True)

class InteractionProcessorBase(
    Generic[TInteraction, TInteractable],
    IInteractionProcessor[TInteraction],
    metaclass=ABCMeta
):
    """Abstract base class for an interaction processor."""

    def __init__(
        self,
        action_processor: IActionProcessor,
        log: LogInterface,
        workflow_execution_rules: Tuple[IWorkflowExecutionRule, ...]
    ) -> None:
        super().__init__()
        self.__action_processor = action_processor
        self.__log = log.with_name("Discord", type(self).__name__)
        self.__workflow_execution_rules = workflow_execution_rules

    async def process(self, interaction: TInteraction) -> None:
        workflow, interactable, arguments = InteractionProcessorBase.__unpack_descriptor(
            self._get_interactable_descriptor(interaction)
        )
        if not workflow or not interactable:
            await self.__action_processor.process(
                interaction,
                ReplyAction(content="I couldn't execute your command, because it's invalid."),
                DeferType.NONE,
                True
            )
            return

        self.__log.trace(f"Processing interactable... {{ Interactable = {interactable.describe()} }}")
        start_time = time.perf_counter()
        if interactable.defer_type == DeferType.DEFER_MESSAGE_CREATION:
            await interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        elif interactable.defer_type == DeferType.DEFER_MESSAGE_UPDATE:
            await interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)

        context = await self._get_interaction_context(interaction)
        if await self.__try_halt_interactable(interaction, workflow, interactable, context):
            return

        response = await interactable.callback(workflow, context, **arguments)
        await self.__action_processor.process(
            interaction,
            response.action,
            interactable.defer_type,
            interactable.is_ephemeral
        )
        # TODO Interactable executed events.
        # await self.__on_command_executed(command, interaction, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Processed command. {{ Interactable = {interactable.describe()}, Elapsed = {elapsed_time} }}")

    @abstractmethod
    def _get_interactable_descriptor(
        self,
        interaction: TInteraction
    ) -> InteractionDescriptor[TInteractable]:
        ...

    @abstractmethod
    def _get_interaction_context(
        self,
        interaction: TInteraction
    ) -> Coroutine[Any, Any, InteractionContext]:
        ...

    @staticmethod
    def __unpack_descriptor(
        descriptor: InteractionDescriptor[TInteractable]
    ) -> Tuple[Optional[IWorkflow], Optional[TInteractable], Dict[str, Any]]:
        return (
            descriptor.workflow,
            descriptor.interactable,
            descriptor.arguments
        )

    async def __try_halt_interactable(
        self,
        interaction: TInteraction,
        workflow: IWorkflow,
        interactable: TInteractable,
        context: InteractionContext
    ) -> bool:
        for rule in self.__workflow_execution_rules:
            if await rule.should_halt(workflow, interactable, context):
                self.__log.debug(f"Interactable has been halted. {{ Interactable = {interactable}, UserId = {context.author_id}, Rule = {type(rule).__name__} }}")
                await self.__action_processor.process(
                    interaction,
                    ReplyAction(
                        content="You're not allowed to use this command."
                    ),
                    interactable.defer_type
                )
                return True
        return False
