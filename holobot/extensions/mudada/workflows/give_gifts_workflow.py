from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    InteractionResponse, Option, StringOption
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import (
    MUDADA_SERVER_ID, VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME
)
from holobot.extensions.mudada.models import Transaction
from holobot.extensions.mudada.repositories import ITransactionRepository, IWalletRepository
from holobot.extensions.mudada.workflows.decorators import requires_event
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

_GIFT_COUNT_MAX: int = 1_000_000_000
_GIFT_COUNT_PER_USER_MAX: int = 10_000
_GIFT_COUNT_PER_USER_MIN: int = 5_000
_MESSAGE_LENGTH_MAX: int = 120

@injectable(IWorkflow)
class GiveGiftsWorkflow(WorkflowBase):
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
        name="give",
        description="Gives the specified number of gifts to a user of your choice.",
        options=(
            Option("user", "The user you'd like to give gifts to.", OptionType.USER),
            Option("number", "The number of gifts you'd like to give.", OptionType.INTEGER),
            StringOption("message", "An optional message. This replaces any previous messages.", OptionType.STRING, False, max_length=_MESSAGE_LENGTH_MAX)
        ),
        server_ids={MUDADA_SERVER_ID},
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        is_ephemeral=True
    )
    async def give_gifts(
        self,
        context: InteractionContext,
        user: int,
        number: int,
        message: str | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if number < 1 or number > _GIFT_COUNT_MAX:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.mudada.give_gifts_workflow.invalid_gift_count_error",
                    {
                        "min": 1,
                        "max": _GIFT_COUNT_MAX
                    }
                )
            )

        if message and len(message) > _MESSAGE_LENGTH_MAX:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.mudada.give_gifts_workflow.message_too_long_error",
                    {
                        "max_length": _MESSAGE_LENGTH_MAX
                    }
                )
            )

        target_user_id = str(user)
        if target_user_id == context.author_id:
            return self._reply(content=self.__i18n.get("extensions.mudada.give_gifts_workflow.self_transfer_error"))

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            wallet = await self.__wallet_repository.get(context.author_id)
            if not wallet or wallet.amount < number:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.give_gifts_workflow.not_enough_gifts_error",
                        {
                            "amount": wallet.amount if wallet else 0
                        }
                    )
                )

            wallet.amount -= number
            await self.__wallet_repository.update(wallet)

            transaction = await self.__transaction_repository.get_by_users(context.author_id, target_user_id)
            if transaction:
                if transaction.is_finalized:
                    return self._reply(
                        content=self.__i18n.get(
                            "extensions.mudada.give_gifts_workflow.gift_finalized_already_error",
                            {
                                "user_id": target_user_id
                            }
                        ),
                        suppress_user_mentions=True
                    )

                if transaction.amount + number > _GIFT_COUNT_PER_USER_MAX:
                    return self.__create_gift_amount_error_response(target_user_id, transaction.amount)

                transaction.amount += number
                transaction.message = message or transaction.message
                await self.__transaction_repository.update(transaction)
            else:
                if number > _GIFT_COUNT_PER_USER_MAX or number < _GIFT_COUNT_PER_USER_MIN:
                    return self.__create_gift_amount_error_response(target_user_id, 0)

                transaction = Transaction(
                    owner_id=context.author_id,
                    target_id=target_user_id,
                    amount=number,
                    message=message
                )
                await self.__transaction_repository.add(transaction)

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.give_gifts_workflow.successful_transaction",
                {
                    "user_id": target_user_id,
                    "amount": number,
                    "target_amount": transaction.amount,
                    "amount_left": wallet.amount
                }
            ),
            suppress_user_mentions=True
        )

    def __create_gift_amount_error_response(
        self,
        target_user_id: str,
        amount: int
    ) -> InteractionResponse:
        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.give_gifts_workflow.too_many_gifts_given_error"
                if amount > 0
                else "extensions.mudada.give_gifts_workflow.too_many_gifts_error",
                {
                    "user_id": target_user_id,
                    "amount": amount,
                    "max_amount": _GIFT_COUNT_PER_USER_MAX,
                    "min_amount": _GIFT_COUNT_PER_USER_MIN
                }
            ),
            suppress_user_mentions=True
        )
