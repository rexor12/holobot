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
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
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
        descriptor = self._get_interactable_descriptor(interaction)
        if not descriptor.workflow or not descriptor.interactable:
            await self.__action_processor.process(
                interaction,
                ReplyAction(content="I couldn't execute your command, because it's invalid."),
                DeferType.NONE,
                True
            )
            return

        self.__log.trace(f"Processing interactable... {{ Interactable = {descriptor.interactable.describe()} }}")
        start_time = time.perf_counter()

        context = self._get_interaction_context(interaction)
        if await self.__try_halt_interactable(
            interaction,
            descriptor.workflow,
            descriptor.interactable,
            descriptor.initiator_id,
            descriptor.bound_user_id,
            context
        ):
            return

        if descriptor.interactable.defer_type == DeferType.DEFER_MESSAGE_CREATION:
            await interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        elif descriptor.interactable.defer_type == DeferType.DEFER_MESSAGE_UPDATE:
            await interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)

        response = await descriptor.interactable.callback(
            descriptor.workflow,
            context,
            **descriptor.arguments
        )
        await self.__action_processor.process(
            interaction,
            response.action,
            descriptor.interactable.defer_type,
            descriptor.interactable.is_ephemeral
        )

        await self._on_interaction_processed(interaction, descriptor.interactable, response)

        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        self.__log.debug(f"Processed command. {{ Interactable = {descriptor.interactable.describe()}, Elapsed = {elapsed_time} }}")

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
    ) -> InteractionContext:
        ...

    @abstractmethod
    def _on_interaction_processed(
        self,
        interaction: TInteraction,
        interactable: TInteractable,
        response: InteractionResponse
    ) -> Coroutine[Any, Any, None]:
        ...

    async def __try_halt_interactable(
        self,
        interaction: TInteraction,
        workflow: IWorkflow,
        interactable: TInteractable,
        initiator_id: str,
        bound_user_id: str,
        context: InteractionContext
    ) -> bool:
        if interactable.is_bound and initiator_id != bound_user_id:
            self.__log.debug(f"Interactable has been halted. {{ Interactable = {interactable}, UserId = {context.author_id}, Reason = BoundUserMismatch }}")
            await self.__action_processor.process(
                interaction,
                ReplyAction(
                    content="You're not allowed to interact with that message."
                ),
                DeferType.NONE,
                True
            )
            return True

        for rule in self.__workflow_execution_rules:
            if await rule.should_halt(workflow, interactable, context):
                self.__log.debug(f"Interactable has been halted. {{ Interactable = {interactable}, UserId = {context.author_id}, Rule = {type(rule).__name__} }}")
                await self.__action_processor.process(
                    interaction,
                    ReplyAction(
                        content="You're not allowed to use this command."
                    ),
                    DeferType.NONE,
                    True
                )
                return True

        return False
