from holobot.discord.sdk.models import Embed, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, Paginator, PaginatorState, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.decorators import autocomplete, command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext, View
from holobot.extensions.general.enums import GrantItemOutcome
from holobot.extensions.general.exceptions import ShopItemNotFoundError
from holobot.extensions.general.managers import IShopManager, IUserItemManager
from holobot.extensions.general.options import GeneralOptions
from holobot.extensions.general.repositories import ICurrencyRepository
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.extensions.general.sdk.wallets.exceptions import (
    CurrencyNotFoundException, NotEnoughMoneyException, WalletNotFoundException
)
from holobot.sdk.configs import IOptions
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import localize
from holobot.sdk.ioc.decorators import injectable
from .utils import autocomplete_global_shop, autocomplete_shop

_SHOP_ITEM_COUNT_MAX = 5

@injectable(IWorkflow)
class BrowseShopsWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        options: IOptions[GeneralOptions],
        shop_manager: IShopManager,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_item_manager: IUserItemManager
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__options = options
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
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=localize("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__create_shop_view(
            ShopId(server_id=context.server_id, shop_id=int(shop_id)),
            0,
            context.author_id
        )

        return self._reply(
            content=content,
            embed=embed,
            components=components
        )

    @command(
        group_name="shop",
        name="viewglobal",
        description="Displays the selected globally available shop's contents.",
        options=(
            Option("shop", "The shop you wish to view.", OptionType.STRING, is_autocomplete=True, argument_name="shop_id"),
        )
    )
    async def view_global_shop(
        self,
        context: InteractionContext,
        shop_id: str
    ) -> InteractionResponse:
        content, embed, components = await self.__create_shop_view(
            ShopId(server_id=0, shop_id=int(shop_id)),
            0,
            context.author_id
        )

        return self._reply(
            content=content,
            embed=embed,
            components=components
        )

    @component(
        identifier="vshop",
        is_bound=True
    )
    async def view_shop2(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or (shop_id := get_custom_int(state.custom_data, "s")) is None
            or (is_global := get_custom_int(state.custom_data, "g")) is None
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )

        server_id = 0 if is_global else context.server_id
        content, embed, components = await self.__create_shop_view(
            ShopId(server_id=server_id, shop_id=shop_id),
            0,
            context.author_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(
        identifier="sibpag",
        is_bound=True
    )
    async def paginate_shop(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if (
            (shop_id := get_custom_int(state.custom_data, "s")) is None
            or (is_global := get_custom_int(state.custom_data, "g")) is None
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )

        if is_global:
            server_id = 0
        elif not isinstance(context, ServerChatInteractionContext):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )
        else:
            server_id = context.server_id

        content, embed, components = await self.__create_shop_view(
            ShopId(server_id=server_id, shop_id=shop_id),
            max(state.current_page, 0),
            context.author_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(
        identifier="sbuyi",
        is_bound=True
    )
    async def buy_item(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or (shop_id := get_custom_int(state.custom_data, "s")) is None
            or (item_id := get_custom_int(state.custom_data, "i")) is None
            or (is_global := get_custom_int(state.custom_data, "g")) is None
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
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
                return self._edit_message(
                    content=localize("extensions.general.browse_shops_workflow.item_owned_already_error"),
                    embed=None,
                    components=self.__create_view_shop_button(
                        shop_id,
                        is_global != 0,
                        state.owner_id
                    )
                )

            if transaction_info.exchange_info is None:
                return self._edit_message(
                    content=localize("extensions.general.browse_shops_workflow.purchase_free"),
                    embed=None,
                    components=self.__create_view_shop_button(
                        shop_id,
                        is_global != 0,
                        state.owner_id
                    )
                )

            exchange_info = transaction_info.exchange_info
            transaction_cost = exchange_info.previous_amount - exchange_info.new_amount
            currency_display_info = await self.__currency_repository.get_display_info(
                exchange_info.currency_id
            )

            return self._edit_message(
                content=localize(
                    "extensions.general.browse_shops_workflow.purchase",
                    {
                        "item_name": item_display_info.name,
                        "item_count": transaction_info.item_count,
                        "transaction_cost": transaction_cost,
                        "currency_emoji_name": currency_display_info.emoji_name,
                        "currency_emoji_id": currency_display_info.emoji_id,
                        "currency_left": exchange_info.new_amount
                    }
                ),
                embed=None,
                components=self.__create_view_shop_button(
                    shop_id,
                    is_global != 0,
                    state.owner_id
                )
            )
        except (NotEnoughMoneyException, WalletNotFoundException, CurrencyNotFoundException):
            return self._edit_message(
                content=localize("extensions.general.browse_shops_workflow.not_enough_money_error"),
                embed=None,
                components=self.__create_view_shop_button(
                    shop_id,
                    is_global != 0,
                    state.owner_id
                )
            )
        except ShopItemNotFoundError:
            return self._edit_message(
                content=localize("extensions.general.browse_shops_workflow.missing_item_error"),
                embed=None,
                components=self.__create_view_shop_button(
                    shop_id,
                    is_global != 0,
                    state.owner_id
                )
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

        return self._autocomplete(
            await autocomplete_shop(
                self.__shop_manager,
                context,
                target_option
            )
        )

    @autocomplete(
        group_name="shop",
        command_name="viewglobal",
        options=("shop",)
    )
    async def autocomplete_global_shop(
        self,
        context: InteractionContext,
        options: tuple[AutocompleteOption, ...],
        target_option: AutocompleteOption
    ) -> InteractionResponse:
        return self._autocomplete(
            await autocomplete_global_shop(
                self.__shop_manager,
                target_option
            )
        )

    def __create_view_shop_button(
        self,
        shop_id: int,
        is_global: bool,
        owner_id: int
    ) -> Button:
        return Button(
            id="vshop",
            owner_id=owner_id,
            text=localize(
                "extensions.general.browse_shops_workflow.view_shop_button"
            ),
            custom_data={
                "s": str(shop_id),
                "g": "1" if is_global else "0"
            }
        )

    async def __create_shop_view(
        self,
        shop_id: ShopId,
        page_index: int,
        owner_id: int
    ) -> View:
        shop_data = await self.__shop_manager.paginate_shop(
            shop_id,
            page_index,
            _SHOP_ITEM_COUNT_MAX
        )
        if not shop_data.items and page_index != 0:
            page_index = 0
            shop_data = await self.__shop_manager.paginate_shop(
                shop_id,
                page_index,
                _SHOP_ITEM_COUNT_MAX
            )

        if not shop_data.items:
            return View(
                content=localize(
                    "extensions.general.browse_shops_workflow.shop_empty_error",
                    {
                        "shop_name": shop_data.name
                    }
                )
            )

        is_global_flag = "1" if not shop_id.server_id else "0"

        return View(
            embed=Embed(
                title=localize(
                    "extensions.general.browse_shops_workflow.shop_title",
                    {
                        "shop_name": shop_data.name
                    }
                ),
                description="\n".join(
                    localize(
                        "extensions.general.browse_shops_workflow.item_description",
                        {
                            "index": item_index + 1,
                            "item_name": item.item_info.name,
                            "item_count": item.count,
                            "item_price": item.price,
                            "currency_emoji_name": item.currency_emoji_name,
                            "currency_emoji_id": item.currency_emoji_id
                        }
                    )
                    for item_index, item in enumerate(shop_data.items)
                ),
                thumbnail_url=self.__options.value.ShopEmbedThumbnailUrl,
                footer=EmbedFooter(
                    text=localize(
                        "extensions.general.browse_shops_workflow.shop_footer"
                    )
                )
            ),
            components=[
                StackLayout(
                    id="slsitems",
                    children=[
                        Button(
                            id="sbuyi",
                            owner_id=owner_id,
                            text=localize(
                                "extensions.general.browse_shops_workflow.buy_button",
                                {
                                    "index": item_index + 1
                                }
                            ),
                            custom_data={
                                "s": str(shop_id.shop_id),
                                "i": str(item.item_id.serial_id),
                                "g": is_global_flag
                            }
                        )
                        for item_index, item in enumerate(shop_data.items)
                    ]
                ),
                Paginator(
                    id="sibpag",
                    owner_id=owner_id,
                    current_page=page_index,
                    page_size=shop_data.page_size,
                    total_count=shop_data.item_count,
                    custom_data={
                        "s": str(shop_id.shop_id),
                        "g": is_global_flag
                    }
                )
            ]
        )
