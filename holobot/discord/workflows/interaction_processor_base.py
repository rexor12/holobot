from abc import ABCMeta, abstractmethod
from collections.abc import Coroutine, Generator
from types import coroutine
from typing import Any, Generic, TypeVar, cast

import hikari

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.sdk.database.exceptions import SerializationError
from holobot.sdk.diagnostics import IExecutionContext, IExecutionContextFactory
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.logging import ILoggerFactory
from .iinteraction_processor import IInteractionProcessor, TInteraction
from .models import InteractionDescriptor

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
        workflow_execution_rules: tuple[IWorkflowExecutionRule, ...]
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
                self.__log.exception("A Discord HTTP error occurred while processing an interaction", **execution_data)
                await self.__try_send_error_response(interaction, execution_data)
            except SerializationError:
                execution_data["has_exception"] = True
                self.__log.trace("A database serialization error occurred while processing an interaction", **execution_data)
                await self.__try_send_error_response(
                    interaction,
                    execution_data,
                    "database_serialization_error"
                )
            except Exception:
                # Don't propagate to the framework, better log it here.
                execution_data["has_exception"] = True
                self.__log.exception("An unhandled exception occurred while processing an interaction", **execution_data)
                await self.__try_send_error_response(interaction, execution_data)

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
        descriptor: InteractionDescriptor[TInteractable],
        response: InteractionResponse
    ) -> Coroutine[Any, Any, None]:
        ...

    async def _send_error_response(
        self,
        interaction: TInteraction,
        localization_key: str = "interactions.unhandled_interaction_error"
    ) -> None:
        await self.__action_processor.process(
            interaction,
            ReplyAction(
                content=self.__i18n_provider.get(localization_key)
            ),
            DeferType.NONE,
            True
        )

    @staticmethod
    def _resolve_argument(
        value: hikari.Snowflake | str | int | bool | None,
        option_type: hikari.OptionType | int
    ) -> str | int | bool | None:
        if value is None:
            return value

        if isinstance(option_type, int):
            option_type = hikari.OptionType(option_type)

        match option_type, value:
            case (hikari.OptionType.STRING, str()):
                return value
            case (hikari.OptionType.BOOLEAN, bool()):
                return value
            case (hikari.OptionType.INTEGER, int()):
                return value
            case (hikari.OptionType.FLOAT, float()):
                return value
            case (hikari.OptionType.USER, int()):
                return value
            case (hikari.OptionType.USER, hikari.Snowflake()):
                # Casting is needed because Pylance doesn't recognize the type.
                return int(cast(hikari.Snowflake, value))
            case (_, _):
                raise ArgumentError(
                    "value",
                    (
                        f"Cannot resolve value of type '{type(value).__name__}'"
                        f" of option type '{option_type}'."
                    )
                )

    async def __process_interaction(
        self,
        interaction: TInteraction,
        execution_context: IExecutionContext,
        execution_data: dict[str, Any]
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
            execution_data["response_processed"] = True

        with execution_context.start("Post-processing performed"):
            await self._on_interaction_processed(
                interaction,
                descriptor,
                response
            )

    @coroutine
    def __try_create_initial_response(
        self,
        interaction: TInteraction,
        interactable: TInteractable
    ) -> Generator[Any, Any, None]:
        if not isinstance(interaction, hikari.MessageResponseMixin):
            return

        match interactable.defer_type:
            case DeferType.DEFER_MESSAGE_CREATION:
                yield from interaction.create_initial_response(
                    hikari.ResponseType.DEFERRED_MESSAGE_CREATE,
                    flags=hikari.MessageFlag.EPHEMERAL if interactable.is_ephemeral else hikari.UNDEFINED
                )
            case DeferType.DEFER_MESSAGE_UPDATE:
                yield from interaction.create_initial_response(
                    hikari.ResponseType.DEFERRED_MESSAGE_UPDATE,
                    flags=hikari.MessageFlag.EPHEMERAL if interactable.is_ephemeral else hikari.UNDEFINED
                )
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
            should_halt, message = await rule.should_halt(workflow, interactable, context)
            if should_halt:
                self.__log.debug(
                    "Interactable has been halted",
                    interactable=str(interactable),
                    user_id=context.author_id,
                    rule=type(rule).__name__
                )
                await self.__action_processor.process(
                    interaction,
                    ReplyAction(
                        content=message or self.__i18n_provider.get(
                            "interactions.halted_interaction_error"
                        )
                    ),
                    DeferType.NONE,
                    True
                )
                return True

        return False

    async def __try_send_error_response(
        self,
        interaction: TInteraction,
        execution_data: dict[str, Any],
        localization_key: str = "interactions.unhandled_interaction_error"
    ) -> None:
        if execution_data.get("response_processed", False):
            # The interaction has been acknowledged only,
            # therefore a second response cannot be sent.
            return

        try:
            await self._send_error_response(interaction, localization_key)
        except Exception as error:
            self.__log.debug(
                "Failed to send the default interaction error response",
                exception=error
            )
