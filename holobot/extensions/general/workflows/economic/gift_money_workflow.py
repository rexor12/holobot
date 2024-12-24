from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import autocomplete, command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models.items import CurrencyItem, UserItem
from holobot.extensions.general.repositories import ICurrencyRepository, IUserItemRepository
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.extensions.general.sdk.wallets.managers import IWalletManager
from holobot.extensions.general.workflows.economic.utils import get_currency_autocomplete_choices
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.identification import IHoloflakeProvider
from holobot.sdk.ioc.decorators import injectable

_MONEY_AMOUNT_MAX: int = 1_000_000_000
_AUTOCOMPLETE_COUNT_MAX: int = 5

@injectable(IWorkflow)
class GiftMoneyWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        holoflake_provider: IHoloflakeProvider,
        i18n_provider: II18nProvider,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_item_repository: IUserItemRepository,
        wallet_manager: IWalletManager
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__holoflake_provider = holoflake_provider
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_item_repository = user_item_repository

    @command(
        group_name="economic",
        subgroup_name="money",
        name="gift",
        description="Gifts the specified amount of your money to a user of your choice.",
        options=(
            Option("user", "The user you'd like to give money to.", OptionType.USER),
            Option("amount", "The amount of money you'd like to give.", OptionType.INTEGER),
            Option("currency", "The type of money you'd like to give.", OptionType.STRING, is_autocomplete=True)
        ),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def gift_money(
        self,
        context: InteractionContext,
        user: int,
        amount: int,
        currency: str
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if user == context.author_id:
            return self._reply(
                content=self.__i18n.get("extensions.general.gift_money_workflow.cannot_gift_to_self_error")
            )

        if amount > _MONEY_AMOUNT_MAX:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.gift_money_workflow.too_much_money_error",
                    {
                        "max_amount": _MONEY_AMOUNT_MAX
                    }
                )
            )

        currency_id = int(currency)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            currency_item = await self.__currency_repository.try_get_by_server(
                currency_id,
                context.server_id,
                True
            )
            if not currency_item:
                return self._reply(
                    content=self.__i18n.get("extensions.general.gift_money_workflow.invalid_currency_error")
                )

            if not currency_item.is_tradable:
                return self._reply(
                    content=self.__i18n.get("extensions.general.gift_money_workflow.currency_untradable_error")
                )

            own_wallet = await self.__user_item_repository.get_wallet(
                context.author_id,
                currency_item.server_id or 0,
                currency_id
            )
            if not own_wallet or own_wallet.item.count < amount:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.gift_money_workflow.not_enough_money_error",
                        {
                            "amount": own_wallet.item.count if own_wallet else 0,
                            "emoji_id": currency_item.emoji_id,
                            "emoji_name": currency_item.emoji_name
                        }
                    )
                )

            target_wallet = await self.__user_item_repository.get_wallet(
                user,
                currency_item.server_id or 0,
                currency_id
            )
            if target_wallet:
                target_wallet.item.count += amount
                await self.__user_item_repository.update(target_wallet)
            else:
                target_wallet = UserItem(
                    identifier=UserItemId(
                        server_id=currency_item.server_id or 0,
                        user_id=user,
                        serial_id=self.__holoflake_provider.get_next_id()
                    ),
                    item=CurrencyItem(
                        count=amount,
                        currency_id=currency_id
                    )
                )
                await self.__user_item_repository.add(target_wallet)

            own_wallet.item.count -= amount
            await self.__user_item_repository.update(own_wallet)

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.gift_money_workflow.successfully_gifted_money",
                {
                    "target_user_id": target_wallet.identifier.user_id,
                    "user_id": own_wallet.identifier.user_id,
                    "amount": amount,
                    "emoji_id": currency_item.emoji_id,
                    "emoji_name": currency_item.emoji_name
                }
            )
        )

    @autocomplete(
        group_name="economic",
        subgroup_name="money",
        command_name="gift",
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
                True
            )
        )
