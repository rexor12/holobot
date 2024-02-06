from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import MUDADA_SERVER_ID
from holobot.extensions.mudada.repositories import IWalletRepository
from holobot.extensions.mudada.workflows.decorators import requires_event
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

@injectable(IWorkflow)
class ShowWalletWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        wallet_repository: IWalletRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__wallet_repository = wallet_repository

    @command(
        group_name="mudada",
        name="wallet",
        description="Displays your wallet's contents.",
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=10),
        server_ids={MUDADA_SERVER_ID},
        is_ephemeral=True
    )
    async def show_wallet(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        wallet = await self.__wallet_repository.get(context.author_id)
        if not wallet:
            return self._reply(
                content=self.__i18n.get("extensions.mudada.show_wallet_workflow.empty_wallet_error")
            )

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.show_wallet_workflow.wallet_message",
                {
                    "amount": wallet.amount
                }
            )
        )
