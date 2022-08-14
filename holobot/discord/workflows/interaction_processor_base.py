from abc import ABCMeta, abstractmethod
from types import coroutine
from typing import Any, Coroutine, Dict, Generator, Generic, Tuple, TypeVar

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
from holobot.sdk.diagnostics import IExecutionContext, IExecutionContextFactory
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.logging import ILoggerFactory

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
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        execution_context_factory: IExecutionContextFactory,
        workflow_execution_rules: Tuple[IWorkflowExecutionRule, ...]
    ) -> None:
        super().__init__()
        self.__action_processor = action_processor
        self.__i18n_provider = i18n_provider
        self.__log = logger_factory.create(type(self))
        self.__execution_context_factory = execution_context_factory
        self.__workflow_execution_rules = workflow_execution_rules

    async def process(self, interaction: TInteraction) -> None:
        execution_data = {}
        with self.__execution_context_factory.create("Processed interactable", "Parent", execution_data) as context:
            try:
                await self.__process_interaction(interaction, context, execution_data)
            except hikari.ClientHTTPResponseError:
                # An expected exception but log it anyway to be aware of the frequency.
                execution_data["has_exception"] = True
                self.__log.exception("A Discord HTTP error occurred while processing an interaction")
            except Exception:
                # Don't propagate to the framework, better log it here.
                execution_data["has_exception"] = True
                self.__log.exception("An unhandled exception occurred while processing an interaction")

    async def __process_interaction(
        self,
        interaction: TInteraction,
        execution_context: IExecutionContext,
        execution_data: Dict[str, Any]
    ) -> None:
        descriptor = self._get_interactable_descriptor(interaction)
        execution_data["initiator_id"] = descriptor.initiator_id
        execution_data["bound_user_id"] = descriptor.bound_user_id
        with execution_context.start("Invalid interaction checked"):
            if await self.__try_halt_on_invalid_interaction(interaction, descriptor):
                execution_data["halt_reason"] = "invalid interaction"
                return

        # Redefining here, because these are now guaranteed not to be None
        # by the __try_halt_on_invalid_interaction method.
        workflow: IWorkflow = descriptor.workflow  # type: ignore
        interactable: TInteractable = descriptor.interactable  # type: ignore

        execution_data["interactable"] = str(interactable)
        context = self._get_interaction_context(interaction)
        with execution_context.start("User mismatch checked"):
            if await self.__try_halt_on_user_mismatch(interaction, interactable, descriptor.initiator_id, descriptor.bound_user_id):
                execution_data["halt_reason"] = "user mismatch"
                return

        with execution_context.start("Rules checked"):
            if await self.__try_halt_by_rule(interaction, workflow, interactable, context):
                execution_data["halt_reason"] = "rule"
                return

        with execution_context.start("Initial response sent"):
            await self.__try_create_initial_response(interaction, interactable)

        with execution_context.start("Interactable processed"):
            response = await interactable.callback(
                descriptor.workflow,
                context,
                **descriptor.arguments
            )

        execution_data["response_action"] = type(response.action).__name__
        with execution_context.start("Response sent"):
            await self.__action_processor.process(
                interaction,
                response.action,
                interactable.defer_type,
                interactable.is_ephemeral
            )

        with execution_context.start("Post-processing performed"):
            await self._on_interaction_processed(interaction, interactable, response)

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

    @coroutine
    def __try_create_initial_response(
        self,
        interaction: TInteraction,
        interactable: TInteractable
    ) -> Generator[Any, Any, None]:
        match interactable.defer_type:
            case DeferType.DEFER_MESSAGE_CREATION:
                yield from interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
            case DeferType.DEFER_MESSAGE_UPDATE:
                yield from interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)
            case _: yield

    async def __try_halt_on_invalid_interaction(
        self,
        interaction: TInteraction,
        descriptor: InteractionDescriptor[TInteractable]
    ) -> bool:
        if descriptor.workflow and descriptor.interactable:
            return False

        await self.__action_processor.process(
            interaction,
            ReplyAction(content=self.__i18n_provider.get("interactions.invalid_interaction_error")),
            DeferType.NONE,
            True
        )
        return True

    async def __try_halt_on_user_mismatch(
        self,
        interaction: TInteraction,
        interactable: TInteractable,
        initiator_id: str,
        bound_user_id: str
    ) -> bool:
        if not interactable.is_bound or initiator_id == bound_user_id:
            return False

        self.__log.debug(
            "Interactable has been halted",
            interactable=str(interactable),
            user_id=initiator_id,
            reason="BoundUserMismatch"
        )
        await self.__action_processor.process(
            interaction,
            ReplyAction(
                content=self.__i18n_provider.get("interactions.unbound_interaction_user_error")
            ),
            DeferType.NONE,
            True
        )
        return True

    async def __try_halt_by_rule(
        self,
        interaction: TInteraction,
        workflow: IWorkflow,
        interactable: TInteractable,
        context: InteractionContext
    ) -> bool:
        for rule in self.__workflow_execution_rules:
            if await rule.should_halt(workflow, interactable, context):
                self.__log.debug(
                    "Interactable has been halted",
                    interactable=str(interactable),
                    user_id=context.author_id,
                    rule=type(rule).__name__
                )
                await self.__action_processor.process(
                    interaction,
                    ReplyAction(
                        content=self.__i18n_provider.get("interactions.halted_interaction_error")
                    ),
                    DeferType.NONE,
                    True
                )
                return True

        return False
