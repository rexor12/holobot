from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import AutocompleteChoice, Embed, InteractionContext
from holobot.discord.sdk.utils.string_utils import escape_user_text
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables import Autocomplete
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentStyle, Paginator, PaginatorState, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.decorators import autocomplete, command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, Cooldown, InteractionResponse, Option, StringOption
)
from holobot.discord.sdk.workflows.interactables.views import Modal
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext, View
from holobot.extensions.general.exceptions import TooManyShopsError
from holobot.extensions.general.exceptions.shop_not_found_error import ShopNotFoundError
from holobot.extensions.general.managers import IShopManager
from holobot.extensions.general.options import GeneralOptions
from holobot.extensions.general.repositories import IBadgeRepository, ICurrencyRepository
from holobot.extensions.general.sdk.badges.exceptions import BadgeNotFoundException
from holobot.extensions.general.sdk.badges.models.badge_id import BadgeId
from holobot.extensions.general.sdk.currencies.exceptions import CurrencyNotFoundException
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.sdk.configs import IOptions
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import localize
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.string_utils import try_parse_int
from .utils import autocomplete_shop

_SHOP_ITEM_COUNT_MAX = 5

@injectable(IWorkflow)
class ManageShopsWorkflow(WorkflowBase):
    def __init__(
        self,
        badge_repository: IBadgeRepository,
        currency_repository: ICurrencyRepository,
        options: IOptions[GeneralOptions],
        shop_manager: IShopManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(
            required_permissions=Permission.ADMINISTRATOR
        )

        self.__badge_repository = badge_repository
        self.__currency_repository = currency_repository
        self.__options = options
        self.__shop_manager = shop_manager
        self.__unit_of_work_provider = unit_of_work_provider

        self.__register_autocomplete_shop("shop", "manage", "remove", "shop")
        self.__register_autocomplete_shop("shop", "manage", "addbadge", "shop")
        self.__register_autocomplete_shop("shop", "manage", "changeitems", "shop")

    @command(
        group_name="shop",
        subgroup_name="manage",
        name="create",
        description="Creates a new shop.",
        cooldown=Cooldown(duration=10),
        options=(
            StringOption("name", "The name of the new shop.", argument_name="shop_name", min_length=3, max_length=50),
        )
    )
    async def create_shop(
        self,
        context: InteractionContext,
        shop_name: str
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=localize("interactions.server_only_interaction_error")
            )

        shop_name = escape_user_text(shop_name)

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            try:
                await self.__shop_manager.create_shop(
                    context.server_id,
                    shop_name
                )

                unit_of_work.complete()
            except TooManyShopsError as error:
                if error.shop_count_max == 0:
                    return self._reply(
                        content=localize(
                            "extensions.general.manage_shops_workflow.server_shops_disabled_error"
                        )
                    )

                return self._reply(
                    content=localize(
                        "extensions.general.manage_shops_workflow.too_many_shops_error"
                    )
                )

        return self._reply(
            content=localize(
                "extensions.general.manage_shops_workflow.shop_created_successfully",
                {
                    "shop_name": shop_name
                }
            )
        )

    @command(
        group_name="shop",
        subgroup_name="manage",
        name="remove",
        description="Removes an existing shop.",
        cooldown=Cooldown(duration=10),
        options=(
            StringOption("shop", "The shop to remove.", argument_name="shop_id", is_autocomplete=True),
        )
    )
    async def remove_shop(
        self,
        context: InteractionContext,
        shop_id: str
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=localize("interactions.server_only_interaction_error")
            )

        full_shop_id = ShopId(server_id=context.server_id, shop_id=int(shop_id))
        shop_name = await self.__shop_manager.get_shop_name(full_shop_id)

        return self._reply(
            content=localize(
                "extensions.general.manage_shops_workflow.shop_removed_successfully",
                {
                    "shop_name": shop_name
                }
            ),
            components=StackLayout(
                id="shopman_layout",
                children=[
                    Button(
                        id="sremovesm",
                        owner_id=context.author_id,
                        text=localize("common.buttons.remove"),
                        style=ComponentStyle.DANGER,
                        custom_data={
                            "i": str(full_shop_id.shop_id)
                        }
                    ),
                    Button(
                        id="shopman_remcancel",
                        owner_id=context.author_id,
                        text=localize("common.buttons.cancel")
                    )
                ]
            )
        )

    @component(
        identifier="shopman_remcancel",
        is_bound=True
    )
    async def cancel_removal(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        return self._clear_message(
            content=localize(
                "extensions.general.manage_shops_workflow.shop_removal_cancelled"
            ),
            embed=None,
            components=None
        )

    @component(
        identifier="sremovesm",
        is_bound=True
    )
    async def confirm_removal(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (shop_id := try_parse_int(state.custom_data.get("i", None)))
        ):
            return self._clear_message(
                content=localize("interactions.invalid_interaction_data_error")
            )

        await self.__shop_manager.remove_shop(ShopId(server_id=context.server_id, shop_id=shop_id))

        return self._clear_message(
            content=localize(
                "extensions.general.manage_shops_workflow.shop_removed_successfully"
            )
        )

    @command(
        group_name="shop",
        subgroup_name="manage",
        name="addbadge",
        description="Adds a badge to a shop.",
        cooldown=Cooldown(duration=10),
        options=(
            StringOption("shop", "The shop to modify.", argument_name="shop_id", is_autocomplete=True),
            StringOption("badge", "The badge to add.", argument_name="badge_id", is_autocomplete=True),
            StringOption("currency", "The type of currency used to pay for the item.", argument_name="currency_id", is_autocomplete=True),
            Option("price", "The price of the item.", OptionType.INTEGER, argument_name="currency_amount"),
        )
    )
    async def add_badge_to_shop(
        self,
        context: InteractionContext,
        shop_id: str,
        badge_id: str,
        currency_id: str,
        currency_amount: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=localize("interactions.server_only_interaction_error")
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            try:
                badge_info, currency_info = await self.__shop_manager.add_badge_to_shop(
                    ShopId(server_id=context.server_id, shop_id=int(shop_id)),
                    BadgeId(server_id=context.server_id, badge_id=int(badge_id)),
                    int(currency_id),
                    currency_amount
                )

                unit_of_work.complete()
            except ShopNotFoundError:
                return self._reply(
                    content=localize(
                        "extensions.general.manage_shops_workflow.shop_not_found_error"
                    )
                )
            except BadgeNotFoundException:
                return self._reply(
                    content=localize(
                        "extensions.general.manage_shops_workflow.badge_not_found_error"
                    )
                )
            except CurrencyNotFoundException:
                return self._reply(
                    content=localize(
                        "extensions.general.manage_shops_workflow.currency_not_found_error"
                    )
                )

        return self._reply(
            content=localize(
                "extensions.general.manage_shops_workflow.badge_added_successfully",
                {
                    "badge_name": badge_info.name,
                    "badge_emoji_id": badge_info.emoji_id,
                    "badge_emoji_name": badge_info.emoji_name,
                    "currency_emoji_id": currency_info.emoji_id,
                    "currency_emoji_name": currency_info.emoji_name,
                    "price": currency_amount
                }
            )
        )

    @autocomplete(
        group_name="shop",
        subgroup_name="manage",
        command_name="addbadge",
        options=("badge",)
    )
    async def autocomplete_badge(
        self,
        context: InteractionContext,
        options: tuple[AutocompleteOption, ...],
        target_option: AutocompleteOption
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._autocomplete([])

        badge_infos = await self.__badge_repository.paginate_badge_infos(
            context.server_id,
            target_option.value if isinstance(target_option.value, str) else None,
            0,
            5
        )

        return self._autocomplete([
            AutocompleteChoice(
                name=badge_info.name,
                value=str(badge_info.badge_id.badge_id)
            ) for badge_info in badge_infos.items
        ])

    @autocomplete(
        group_name="shop",
        subgroup_name="manage",
        command_name="addbadge",
        options=("currency",)
    )
    async def autocomplete_currency(
        self,
        context: InteractionContext,
        options: tuple[AutocompleteOption, ...],
        target_option: AutocompleteOption
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._autocomplete([])

        currency_infos = await self.__currency_repository.paginate_currency_infos(
            context.server_id,
            target_option.value if isinstance(target_option.value, str) else None,
            0,
            5
        )

        return self._autocomplete([
            AutocompleteChoice(
                name=badge_info.name,
                value=str(badge_info.currency_id)
            ) for badge_info in currency_infos.items
        ])

    @command(
        group_name="shop",
        subgroup_name="manage",
        name="changeitems",
        description="Displays the item list of a shop for editing.",
        cooldown=Cooldown(duration=10),
        options=(
            StringOption("shop", "The shop to view.", argument_name="shop_id", is_autocomplete=True),
        )
    )
    async def view_shop_items(
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

    @component(
        identifier="sremoveim",
        is_bound=True
    )
    async def remove_shop_item(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or (shop_id := get_custom_int(state.custom_data, "s")) is None
            or (item_id := get_custom_int(state.custom_data, "i")) is None
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )

        # TODO Confirm user intent.
        await self.__shop_manager.remove_shop_item(
            ShopItemId(
                server_id=context.server_id,
                shop_id=shop_id,
                serial_id=item_id
            )
        )

        return self._edit_message(
            content=localize(
                "extensions.general.manage_shops_workflow.shop_item_removed_successfully",
            ),
            embed=None,
            components=self.__create_view_shop_button(
                shop_id,
                state.owner_id
            )
        )

    @component(
        identifier="vshopm",
        is_bound=True
    )
    async def view_shop(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or (shop_id := get_custom_int(state.custom_data, "s")) is None
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__create_shop_view(
            ShopId(server_id=context.server_id, shop_id=shop_id),
            0,
            context.author_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(
        identifier="sibpagm",
        is_bound=True
    )
    async def paginate_shop(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or (shop_id := get_custom_int(state.custom_data, "s")) is None
        ):
            return self._clear_message(
                content=localize("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__create_shop_view(
            ShopId(server_id=context.server_id, shop_id=shop_id),
            max(state.current_page, 0),
            context.author_id
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __autocomplete_shop(
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

    def __register_autocomplete_shop(
        self,
        group_name: str,
        subgroup_name: str,
        name: str,
        option_name: str
    ) -> None:
        self.add_registration(Autocomplete(
            group_name=group_name,
            subgroup_name=subgroup_name,
            name=name,
            options=(option_name,),
            callback=ManageShopsWorkflow.__autocomplete_shop
        ))

    def __create_view_shop_button(
        self,
        shop_id: int,
        owner_id: int
    ) -> Button:
        return Button(
            id="vshopm",
            owner_id=owner_id,
            text=localize(
                "extensions.general.manage_shops_workflow.view_shop_button"
            ),
            custom_data={
                "s": str(shop_id)
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
                    "extensions.general.manage_shops_workflow.shop_empty_error",
                    {
                        "shop_name": shop_data.name
                    }
                )
            )

        remove_item_buttons = StackLayout(id="dummy", children=[])
        for item_index, item in enumerate(shop_data.items):
            remove_item_buttons.children.append(
                Button(
                    id="sremoveim",
                    owner_id=owner_id,
                    style=ComponentStyle.DANGER,
                    text=localize(
                        "extensions.general.manage_shops_workflow.remove_button",
                        {
                            "index": item_index + 1
                        }
                    ),
                    custom_data={
                        "s": str(shop_id.shop_id),
                        "i": str(item.item_id.serial_id)
                    }
                )
            )

        return View(
            embed=Embed(
                title=localize(
                    "extensions.general.manage_shops_workflow.shop_title",
                    {
                        "shop_name": shop_data.name
                    }
                ),
                description="\n".join(
                    localize(
                        "extensions.general.manage_shops_workflow.item_description",
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
                thumbnail_url=self.__options.value.ShopEmbedThumbnailUrl
            ),
            components=[
                remove_item_buttons,
                Paginator(
                    id="sibpagm",
                    owner_id=owner_id,
                    current_page=page_index,
                    page_size=shop_data.page_size,
                    total_count=shop_data.item_count,
                    custom_data={
                        "s": str(shop_id.shop_id)
                    }
                )
            ]
        )
