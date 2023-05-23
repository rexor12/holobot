from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class SayWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        messaging: IMessaging
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__messaging = messaging

    @command(
        name="say",
        description="Repeats the specified text as the bot.",
        options=(
            Option("message", "The message to be repeated."),
        ),
        is_ephemeral=True,
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def say(
        self,
        context: InteractionContext,
        message: str,
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        await self.__messaging.send_channel_message(
            context.server_id,
            context.channel_id,
            message,
            suppress_user_mentions=True
        )

        return self._delete()
