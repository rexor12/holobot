from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import autocomplete, command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.repositories import ICurrencyRepository, IWalletRepository
from holobot.extensions.general.sdk.wallets.models import WalletId
from holobot.extensions.general.workflows.economic.utils import get_currency_autocomplete_choices
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

_AUTOCOMPLETE_COUNT_MAX: int = 5

@injectable(IWorkflow)
class TakeMoneyWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        i18n_provider: II18nProvider,
        unit_of_work_provider: IUnitOfWorkProvider,
        wallet_repository: IWalletRepository
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__wallet_repository = wallet_repository

    @command(
        group_name="economic",
        subgroup_name="money",
        name="take",
        description="Takes the specified amount of money from a user of your choice.",
        options=(
            Option("user", "The user you'd like to give money from.", OptionType.USER),
            Option("amount", "The amount of money you'd like to take.", OptionType.INTEGER),
            Option("currency", "The type of money you'd like to take.", OptionType.STRING, is_autocomplete=True)
        ),
        required_permissions=Permission.ADMINISTRATOR,
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def take_money(
        self,
        context: InteractionContext,
        user: int,
        amount: int,
        currency: str
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if amount < 1:
            return self._reply(
                content=self.__i18n.get("extensions.general.take_money_workflow.too_little_money_error")
            )

        if user is None:
            await self.__wallet_repository.remove_from_all_users(amount)
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.take_money_workflow.successfully_removed_money_from_all"
                )
            )

        currency_id = int(currency)
        wallet_id = WalletId(user_id=user, currency_id=currency_id, server_id=context.server_id)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            currency_item = await self.__currency_repository.try_get_by_server(currency_id, context.server_id, False)
            if not currency_item:
                return self._reply(
                    content=self.__i18n.get("extensions.general.take_money_workflow.invalid_currency_error")
                )

            wallet = await self.__wallet_repository.get(wallet_id)
            if not wallet:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.take_money_workflow.user_has_no_money_error",
                        {
                            "user_id": user
                        }
                    )
                )

            wallet.amount = max(wallet.amount - amount, 0)
            await self.__wallet_repository.update(wallet)
            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.take_money_workflow.successfully_removed_money",
                {
                    "user_id": wallet.identifier.user_id,
                    "amount": wallet.amount,
                    "emoji_id": currency_item.emoji_id,
                    "emoji_name": currency_item.emoji_name
                }
            )
        )

    @autocomplete(
        group_name="economic",
        subgroup_name="money",
        command_name="take",
        options=("currency",)
    )
    async def autocomplete_currency(
        self,
        context: InteractionContext,
        options: tuple[AutocompleteOption, ...],
        target_option: AutocompleteOption
    ) -> InteractionResponse:
        return self._autocomplete(
            await get_currency_autocomplete_choices(
                context,
                options,
                target_option,
                _AUTOCOMPLETE_COUNT_MAX,
                self.__currency_repository,
                False
            )
        )
