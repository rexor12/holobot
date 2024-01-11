from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.repositories import IChannelTimerRepository
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

@injectable(IWorkflow)
class RemoveChannelTimerWorkflow(WorkflowBase):
    def __init__(
        self,
        channel_timer_repository: IChannelTimerRepository,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__channel_timer_repository = channel_timer_repository
        self.__i18n = i18n_provider

    @command(
        group_name="timers",
        name="remove",
        description="Removes any currently active channel timers.",
        required_permissions=Permission.ADMINISTRATOR,
        is_ephemeral=True,
        cooldown=Cooldown(duration=3)
    )
    async def remove_channel_timer(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error"),
                is_ephemeral=True
            )

        count = await self.__channel_timer_repository.remove_all_by_server(context.server_id)

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.remove_channel_timer_workflow.removed_successfully"
                if count > 0
                else "extensions.general.remove_channel_timer_workflow.no_timers_error"
            ),
            is_ephemeral=True
        )
