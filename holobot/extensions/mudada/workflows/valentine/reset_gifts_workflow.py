from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import (
    MUDADA_FEATURE_NAME, VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME
)
from holobot.extensions.mudada.repositories import ITransactionRepository, IWalletRepository
from holobot.extensions.mudada.workflows.decorators import requires_event
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ResetGiftsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        transaction_repository: ITransactionRepository,
        unit_of_work_provider: IUnitOfWorkProvider,
        wallet_repository: IWalletRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__transaction_repository = transaction_repository
        self.__unit_of_work_provider = unit_of_work_provider
        self.__wallet_repository = wallet_repository

    @requires_event(VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME)
    @command(
        group_name="mudada",
        subgroup_name="valentine",
        name="reset",
        description="Resets ALL of your prepared gifts, returning the gifts to you.",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),),
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        is_ephemeral=True
    )
    async def reset_gifts(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            amount_to_return = await self.__transaction_repository.get_total_transaction_amount(
                context.author_id,
                False
            )
            if amount_to_return <= 0:
                return self._reply(
                    content=self.__i18n.get("extensions.mudada.reset_reservations_workflow.nothing_to_return_error")
                )

            wallet = await self.__wallet_repository.get(context.author_id)
            if not wallet:
                raise Exception(f"Cannot find the wallet of user '{context.author_id}'.")

            wallet.amount += amount_to_return
            await self.__wallet_repository.update(wallet)
            await self.__transaction_repository.delete_all_by_user(context.author_id, False)
            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.reset_reservations_workflow.successful_reset",
                {
                    "returned_amount": amount_to_return,
                    "total_amount": wallet.amount
                }
            )
        )
