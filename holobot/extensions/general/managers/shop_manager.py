from collections.abc import AsyncGenerator, Awaitable, Iterable, Sequence
from typing import Any

from holobot.extensions.general.enums import GrantItemOutcome, ItemType
from holobot.extensions.general.exceptions import (
    ShopItemNotFoundError, ShopNotFoundError, UnknownShopItemTypeError
)
from holobot.extensions.general.models.items import (
    BackgroundItem, BadgeItem, CurrencyDisplayInfo, CurrencyItem, UserItem
)
from holobot.extensions.general.models.shops import (
    DetailedShopDisplayInfo, ShopDisplayInfo, ShopItem, ShopItemDisplayInfo, TransactionInfo
)
from holobot.extensions.general.repositories import IBadgeRepository, ICurrencyRepository
from holobot.extensions.general.repositories.shops import IShopItemRepository, IShopRepository
from holobot.extensions.general.repositories.user_profiles import IUserProfileBackgroundRepository
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.extensions.general.sdk.wallets.managers import IWalletManager
from holobot.sdk.chrono import IClock
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils.iterable_utils import extend_async, group_by, select, unique
from .ishop_manager import IShopManager
from .iuser_item_manager import IUserItemManager

@injectable(IShopManager)
class ShopManager(IShopManager):
    def __init__(
        self,
        background_repository: IUserProfileBackgroundRepository,
        badge_repository: IBadgeRepository,
        clock: IClock,
        currency_repository: ICurrencyRepository,
        logger_factory: ILoggerFactory,
        shop_repository: IShopRepository,
        shop_item_repository: IShopItemRepository,
        user_item_manager: IUserItemManager,
        wallet_manager: IWalletManager
    ) -> None:
        super().__init__()
        self.__background_repository = background_repository
        self.__badge_repository = badge_repository
        self.__clock = clock
        self.__currency_repository = currency_repository
        self.__logger = logger_factory.create(ShopManager)
        self.__shop_repository = shop_repository
        self.__shop_item_repository = shop_item_repository
        self.__user_item_manager = user_item_manager
        self.__wallet_manager = wallet_manager
        self.__item_factories = {
            ItemType.CURRENCY: self.__grant_currency,
            ItemType.BADGE: self.__grant_badge,
            ItemType.BACKGROUND: self.__grant_background
        }
        self.__item_display_resolvers = {
            ItemType.CURRENCY: self.__resolve_currency_display_items,
            ItemType.BADGE: self.__resolve_badge_display_items,
            ItemType.BACKGROUND: self.__resolve_background_display_items
        }

    def paginate_shops(
        self,
        server_id: int,
        name_part: str | None,
        page_index: int,
        page_size: int = 5
    ) -> Awaitable[PaginationResult[ShopDisplayInfo]]:
        return self.__shop_repository.paginate_shop_infos(
            server_id,
            name_part,
            page_index,
            page_size
        )

    async def paginate_shop(
        self,
        shop_id: ShopId,
        page_index: int,
        page_size: int = 5
    ) -> DetailedShopDisplayInfo:
        shop = await self.__shop_repository.get(shop_id)
        if not shop:
            raise ShopNotFoundError(shop_id)

        shop_items = await self.__shop_item_repository.paginate(
            shop_id,
            page_index,
            page_size
        )
        if len(shop_items.items) == 0:
            return DetailedShopDisplayInfo(
                name=shop.shop_name,
                page_index=page_index,
                page_size=page_size,
                item_count=0,
                items=[]
            )

        return DetailedShopDisplayInfo(
            name=shop.shop_name,
            page_index=page_index,
            page_size=page_size,
            item_count=shop_items.total_count,
            items=await self.__resolve_item_displays(
                shop_id,
                shop_items.items
            )
        )

    async def buy_item(
        self,
        user_id: int,
        shop_item_id: ShopItemId,
        count: int = 1
    ) -> TransactionInfo:
        shop_item = await self.__shop_item_repository.get(shop_item_id)
        if not shop_item:
            raise ShopItemNotFoundError(shop_item_id)

        if not (factory := self.__item_factories.get(shop_item.item_type)):
            raise UnknownShopItemTypeError(shop_item_id, shop_item.item_type)

        total_item_count = count * shop_item.count
        outcome, granted_item = await factory(user_id, shop_item, total_item_count)
        if shop_item.price_currency_id == 0 or shop_item.price_amount == 0:
            return TransactionInfo(
                outcome=outcome,
                item=granted_item,
                item_count=count
            )

        if outcome == GrantItemOutcome.GRANTED:
            exchange_info = await self.__wallet_manager.take_money(
                user_id,
                shop_item.price_currency_id,
                shop_item_id.server_id,
                shop_item.price_amount,
                False
            )
        else:
            exchange_info = None

        return TransactionInfo(
            outcome=outcome,
            item=granted_item,
            item_count=total_item_count,
            exchange_info=exchange_info
        )

    def __grant_currency(
        self,
        user_id: int,
        shop_item: ShopItem,
        count: int
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        return self.__user_item_manager.grant_item(
            shop_item.identifier.server_id,
            user_id,
            CurrencyItem(
                currency_id=shop_item.item_id1,
                count=count
            )
        )

    def __grant_badge(
        self,
        user_id: int,
        shop_item: ShopItem,
        count: int
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        return self.__user_item_manager.grant_item(
            shop_item.identifier.server_id,
            user_id,
            BadgeItem(
                badge_id=BadgeId(
                    server_id=shop_item.identifier.server_id,
                    badge_id=shop_item.item_id1
                ),
                unlocked_at=self.__clock.now_utc(),
                count=count
            )
        )

    def __grant_background(
        self,
        user_id: int,
        shop_item: ShopItem,
        count: int
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        return self.__user_item_manager.grant_item(
            shop_item.identifier.server_id,
            user_id,
            BackgroundItem(
                background_id=shop_item.item_id1,
                count=count
            )
        )

    async def __resolve_item_displays(
        self,
        shop_id: ShopId,
        shop_items: Sequence[ShopItem]
    ) -> list[ShopItemDisplayInfo]:
        currency_info_by_ids = await self.__resolve_currency_infos(shop_items)
        grouped_items = group_by(shop_items, lambda i: i.item_type)
        item_display_infos = list[ShopItemDisplayInfo]()
        for item_type, items in grouped_items.items():
            if item_type not in self.__item_display_resolvers:
                self.__logger.warning(
                    "Unknown shop item type",
                    item_type=item_type,
                    shop_id=shop_id
                )
                continue

            resolved_infos = self.__item_display_resolvers[item_type](
                shop_id.server_id,
                items,
                currency_info_by_ids
            )

            await extend_async(item_display_infos, resolved_infos)

        return item_display_infos

    async def __resolve_currency_infos(
        self,
        shop_items: Iterable[ShopItem]
    ) -> dict[int, CurrencyDisplayInfo]:
        currency_ids = tuple(unique(select(shop_items, lambda i: i.price_currency_id)))
        currency_infos = await self.__currency_repository.get_display_infos(currency_ids)

        return {
            currency_info.currency_id: currency_info
            for currency_info in currency_infos
        }

    async def __resolve_currency_display_items(
        self,
        server_id: int,
        items: Sequence[ShopItem],
        currency_infos: dict[int, CurrencyDisplayInfo]
    ) -> AsyncGenerator[ShopItemDisplayInfo, Any]:
        item_infos = await self.__currency_repository.get_display_infos(
            tuple(map(lambda i: i.item_id1, items))
        )
        item_info_by_ids = {
            item_info.currency_id: item_info
            for item_info in item_infos
        }
        for item in items:
            if item.item_id1 not in item_info_by_ids:
                self.__logger.warning(
                    "Unresolvable currency shop item",
                    item_type=item.item_type,
                    item_id1=item.item_id1
                )
                continue

            currency_info = currency_infos[item.price_currency_id]

            yield ShopItemDisplayInfo(
                item_id=item.identifier,
                count=item.count,
                currency_emoji_name=currency_info.emoji_name,
                currency_emoji_id=currency_info.emoji_id,
                price=item.price_amount,
                item_info=item_info_by_ids[item.item_id1]
            )

    async def __resolve_badge_display_items(
        self,
        server_id: int,
        items: Sequence[ShopItem],
        currency_infos: dict[int, CurrencyDisplayInfo]
    ) -> AsyncGenerator[ShopItemDisplayInfo, Any]:
        item_infos = await self.__badge_repository.get_display_infos(
            server_id,
            tuple(map(lambda i: i.item_id1, items))
        )
        item_info_by_ids = {
            item_info.badge_id.badge_id: item_info
            for item_info in item_infos
        }
        for item in items:
            if item.item_id1 not in item_info_by_ids:
                self.__logger.warning(
                    "Unresolvable badge shop item",
                    item_type=item.item_type,
                    item_id1=item.item_id1
                )
                continue

            currency_info = currency_infos[item.price_currency_id]

            yield ShopItemDisplayInfo(
                item_id=item.identifier,
                count=item.count,
                currency_emoji_name=currency_info.emoji_name,
                currency_emoji_id=currency_info.emoji_id,
                price=item.price_amount,
                item_info=item_info_by_ids[item.item_id1]
            )

    async def __resolve_background_display_items(
        self,
        server_id: int,
        items: Sequence[ShopItem],
        currency_infos: dict[int, CurrencyDisplayInfo]
    ) -> AsyncGenerator[ShopItemDisplayInfo, Any]:
        item_infos = await self.__background_repository.get_display_infos(
            tuple(map(lambda i: i.item_id1, items))
        )
        item_info_by_ids = {
            item_info.background_id: item_info
            for item_info in item_infos
        }
        for item in items:
            if item.item_id1 not in item_info_by_ids:
                self.__logger.warning(
                    "Unresolvable background shop item",
                    item_type=item.item_type,
                    item_id1=item.item_id1
                )
                continue

            currency_info = currency_infos[item.price_currency_id]

            yield ShopItemDisplayInfo(
                item_id=item.identifier,
                count=item.count,
                currency_emoji_name=currency_info.emoji_name,
                currency_emoji_id=currency_info.emoji_id,
                price=item.price_amount,
                item_info=item_info_by_ids[item.item_id1]
            )
