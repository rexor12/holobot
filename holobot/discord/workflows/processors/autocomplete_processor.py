from collections.abc import Awaitable
from uuid import uuid4

from hikari import AutocompleteInteraction, OptionType

from holobot.discord.actions import IActionProcessor
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import Autocomplete
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, InteractionResponse
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.discord.workflows import (
    IInteractionProcessor, InteractionProcessorBase, IWorkflowRegistry
)
from holobot.discord.workflows.models import InteractionDescriptor
from holobot.sdk.diagnostics import IExecutionContextFactory
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.threading import COMPLETED_TASK

@injectable(IInteractionProcessor[AutocompleteInteraction])
class AutocompleteProcessor(InteractionProcessorBase[AutocompleteInteraction, Autocomplete]):
    def __init__(
        self,
        action_processor: IActionProcessor,
        i18n_provider: II18nProvider,
        log: ILoggerFactory,
        measurement_context_factory: IExecutionContextFactory,
        workflow_registry: IWorkflowRegistry
    ) -> None:
        super().__init__(action_processor, i18n_provider, log, measurement_context_factory, ())
        self.__workflow_registry = workflow_registry

    def _get_interactable_descriptor(
        self,
        interaction: AutocompleteInteraction
    ) -> InteractionDescriptor[Autocomplete]:
        group_name = None
        subgroup_name = None
        command_name = interaction.command_name
        target_option = None
        autocomplete_options = list[AutocompleteOption]()
        options = list(interaction.options) if interaction.options else []
        while options:
            option = options.pop(0)
            match option.type:
                case OptionType.SUB_COMMAND_GROUP:
                    group_name = interaction.command_name
                    subgroup_name = option.name
                    options = list(option.options) if option.options else []
                case OptionType.SUB_COMMAND:
                    group_name = group_name or interaction.command_name
                    command_name = option.name
                    options = list(option.options) if option.options else []
                case _:
                    autocomplete_option = AutocompleteOption(
                        name=option.name,
                        is_focused=option.is_focused,
                        value=InteractionProcessorBase._resolve_argument(
                            option.value,
                            option.type
                        )
                    )
                    if option.is_focused:
                        target_option = autocomplete_option
                    else:
                        autocomplete_options.append(autocomplete_option)

        if not target_option:
            raise ArgumentError(
                "interaction",
                "No option with is_focused=True has been specified."
            )

        invocation_target = self.__workflow_registry.get_autocomplete(
            group_name,
            subgroup_name,
            command_name,
            target_option.name
        )

        return InteractionDescriptor(
            workflow=invocation_target[0] if invocation_target else None,
            interactable=invocation_target[1] if invocation_target else None,
            arguments={
                "options": autocomplete_options,
                "target_option": target_option
            },
            initiator_id=str(interaction.user.id),
            bound_user_id=str(interaction.user.id)
        )

    def _get_interaction_context(
        self,
        interaction: AutocompleteInteraction
    ) -> InteractionContext:
        # TODO Support non-server specific commands.
        if not interaction.guild_id:
            raise NotImplementedError("Non-server specific commands are not supported.")

        return ServerChatInteractionContext(
            request_id=uuid4(),
            author_id=str(interaction.user.id),
            author_name=interaction.user.username,
            author_nickname=interaction.member.nickname if interaction.member else None,
            server_id=str(interaction.guild_id),
            server_name=guild.name if (guild := interaction.get_guild()) else "Unknown Server",
            channel_id=str(interaction.channel_id)
        )

    def _on_interaction_processed(
        self,
        interaction: AutocompleteInteraction,
        descriptor: InteractionDescriptor[Autocomplete],
        response: InteractionResponse
    ) -> Awaitable[None]:
        # Autocomplete interactions have no event listeners.
        return COMPLETED_TASK

    async def _send_error_response(
        self,
        interaction: AutocompleteInteraction,
        localization_key: str = "interactions.unhandled_interaction_error"
    ) -> None:
        await interaction.create_response(())
