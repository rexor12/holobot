from holobot.discord.sdk.models import AutocompleteChoice, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import autocomplete, command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.enums import GrantItemOutcome
from holobot.extensions.general.exceptions import ShopItemNotFoundError
from holobot.extensions.general.managers import IShopManager, IUserItemManager
from holobot.extensions.general.repositories import ICurrencyRepository
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.extensions.general.sdk.wallets.exceptions import (
    CurrencyNotFoundException, NotEnoughMoneyException, WalletNotFoundException
)
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

_AUTOCOMPLETE_COUNT_MAX = 5

@injectable(IWorkflow)
class BuyItemWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        i18n_provider: II18nProvider,
        shop_manager: IShopManager,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_item_manager: IUserItemManager
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__i18n = i18n_provider
        self.__shop_manager = shop_manager
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_item_manager = user_item_manager

    @command(
        group_name="shop",
        name="view",
        description="Displays the selected shop's contents.",
        options=(
            Option("shop", "The shop you wish to view.", OptionType.STRING, is_autocomplete=True, argument_name="shop_id"),
        )
    )
    async def view_shop(
        self,
        context: InteractionContext,
        shop_id: str
    ) -> InteractionResponse:
        raise NotImplementedError

    @command(
        group_name="shop",
        name="buy",
        description="Buys an item from the shop.",
        options=(
            Option("shop_id", "shop_id", OptionType.INTEGER),
            Option("item_id", "item_Id", OptionType.INTEGER),
            Option("is_global", "is_global", OptionType.BOOLEAN),
        )
    )
    async def buy_item(
        self,
        context: InteractionContext,
        shop_id: int,
        item_id: int,
        is_global: bool
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        try:
            server_id = 0 if is_global else context.server_id
            async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
                transaction_info = await self.__shop_manager.buy_item(
                    context.author_id,
                    ShopItemId(
                        server_id=server_id,
                        shop_id=shop_id,
                        serial_id=item_id
                    )
                )

                unit_of_work.complete()

            item_display_info = await self.__user_item_manager.get_item_display_info(
                transaction_info.item.item
            )
            if transaction_info.outcome == GrantItemOutcome.GRANTED_ALREADY:
                return self._reply(
                    content=self.__i18n.get("extensions.general.buy_item_workflow.item_owned_already_error")
                )

            if transaction_info.exchange_info is None:
                return self._reply(
                    content=self.__i18n.get("extensions.general.buy_item_workflow.purchase_free")
                )

            exchange_info = transaction_info.exchange_info
            transaction_cost = exchange_info.previous_amount - exchange_info.new_amount
            currency_display_info = await self.__currency_repository.get_display_info(
                exchange_info.currency_id
            )

            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.buy_item_workflow.purchase",
                    {
                        "item_name": item_display_info.name,
                        "item_count": transaction_info.item_count,
                        "transaction_cost": transaction_cost,
                        "currency_emoji_name": currency_display_info.emoji_name,
                        "currency_emoji_id": currency_display_info.emoji_id,
                        "currency_left": exchange_info.new_amount
                    }
                )
            )
        except (NotEnoughMoneyException, WalletNotFoundException, CurrencyNotFoundException):
            return self._reply(
                content=self.__i18n.get("extensions.general.buy_item_workflow.not_enough_money_error")
            )
        except ShopItemNotFoundError:
            return self._reply(
                content=self.__i18n.get("extensions.general.buy_item_workflow.missing_item_error")
            )

    @autocomplete(
        group_name="shop",
        command_name="view",
        options=("shop",)
    )
    async def autocomplete_shop(
        self,
        context: InteractionContext,
        options: tuple[AutocompleteOption, ...],
        target_option: AutocompleteOption
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._autocomplete([])

        if not isinstance(target_option.value, str) or not target_option.value:
            raise NotImplementedError # TODO (Shops) return "all" server shops

        return self._autocomplete(AutocompleteChoice(
            name="Secret Shop?",
            value="secret-shop-id"
        ))
        raise NotImplementedError
