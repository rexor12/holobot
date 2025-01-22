from collections.abc import Awaitable

from holobot.extensions.general.enums import GrantItemOutcome, ItemType
from holobot.extensions.general.exceptions import (
    ShopItemNotFoundError, ShopNotFoundError, UnknownShopItemTypeError
)
from holobot.extensions.general.models.items import (
    BackgroundItem, BadgeItem, CurrencyItem, UserItem
)
from holobot.extensions.general.models.shops import ShopDisplayInfo, ShopItem, TransactionInfo
from holobot.extensions.general.repositories.shops import IShopItemRepository, IShopRepository
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.extensions.general.sdk.shops.models import ShopId, ShopItemId
from holobot.extensions.general.sdk.wallets.managers import IWalletManager
from holobot.sdk.chrono import IClock
from holobot.sdk.ioc.decorators import injectable
from .ishop_manager import IShopManager
from .iuser_item_manager import IUserItemManager

@injectable(IShopManager)
class ShopManager(IShopManager):
    def __init__(
        self,
        clock: IClock,
        shop_repository: IShopRepository,
        shop_item_repository: IShopItemRepository,
        user_item_manager: IUserItemManager,
        wallet_manager: IWalletManager
    ) -> None:
        super().__init__()
        self.__clock = clock
        self.__shop_repository = shop_repository
        self.__shop_item_repository = shop_item_repository
        self.__user_item_manager = user_item_manager
        self.__wallet_manager = wallet_manager
        self.__item_factories = {
            ItemType.CURRENCY: self.__grant_currency,
            ItemType.BADGE: self.__grant_badge,
            ItemType.BACKGROUND: self.__grant_background
        }

    async def paginate_shop(
        self,
        shop_id: ShopId,
        page_index: int,
        page_size: int = 5
    ) -> ShopDisplayInfo:
        shop = await self.__shop_repository.get(shop_id)
        if not shop:
            raise ShopNotFoundError(shop_id)

        shop_items = await self.__shop_item_repository.paginate(
            shop_id,
            page_index,
            page_size
        )
        if len(shop_items.items) == 0:
            raise ShopNotFoundError(shop_id)

        return ShopDisplayInfo(
            name=shop.shop_name,
            page_index=page_index,
            page_size=page_size,
            item_count=0,
            items=[]
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
