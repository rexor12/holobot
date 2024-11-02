from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
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
from holobot.sdk.logging import ILoggerFactory

@injectable(IWorkflow)
class TakeGiftsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
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
        name="take",
        description="Takes the specified number of gifts from a user of your choice.",
        options=(
            Option("user", "The user you'd like to give gifts to.", OptionType.USER),
            Option("number", "The number of gifts you'd like to give.", OptionType.INTEGER)
        ),
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),),
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        is_ephemeral=True
    )
    async def take_gifts(
        self,
        context: InteractionContext,
        user: int,
        number: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if number < 1:
            return self._reply(content=self.__i18n.get("extensions.mudada.take_gifts_workflow.invalid_gift_count_error"))

        target_user_id = str(user)
        if target_user_id == context.author_id:
            return self._reply(content=self.__i18n.get("extensions.mudada.take_gifts_workflow.self_transfer_error"))

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            transaction = await self.__transaction_repository.get_by_users(context.author_id, target_user_id)
            if not transaction:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.take_gifts_workflow.missing_transaction_error",
                        {
                            "user_id": target_user_id
                        }
                    ),
                    suppress_user_mentions=True
                )

            if transaction.is_finalized:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.take_gifts_workflow.gift_finalized_already_error",
                        {
                            "user_id": target_user_id
                        }
                    ),
                    suppress_user_mentions=True
                )

            wallet = await self.__wallet_repository.get(context.author_id)
            if not wallet:
                raise Exception(f"Cannot find the wallet of user '{context.author_id}'.")

            taken_amount = transaction.amount if transaction.amount < number else number
            wallet.amount += taken_amount
            await self.__wallet_repository.update(wallet)

            transaction.amount -= taken_amount
            if transaction.amount > 0:
                await self.__transaction_repository.update(transaction)
            else:
                await self.__transaction_repository.delete(transaction.identifier)

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.take_gifts_workflow.taken_less_successfully"
                if taken_amount < number
                else "extensions.mudada.take_gifts_workflow.taken_exact_successfully",
                {
                    "user_id": target_user_id,
                    "taken_amount": taken_amount,
                    "total_amount": wallet.amount
                }
            ),
            suppress_user_mentions=True
        )
