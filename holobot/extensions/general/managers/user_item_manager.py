from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from holobot.extensions.general.enums import GrantItemOutcome
from holobot.extensions.general.models.items import (
    BackgroundDisplayInfo, BackgroundItem, BadgeDisplayInfo, BadgeItem, CurrencyDisplayInfo,
    CurrencyItem, ItemBase, ItemDisplayInfoBase, UserItem
)
from holobot.extensions.general.repositories import (
    IBadgeRepository, ICurrencyRepository, IUserItemRepository
)
from holobot.extensions.general.repositories.user_profiles import IUserProfileBackgroundRepository
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.extensions.general.sdk.items.exceptions import InvalidItemTypeException
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.extensions.general.sdk.quests.models import (
    BackgroundQuestReward, BadgeQuestReward, CurrencyQuestReward, QuestRewardBase
)
from holobot.sdk.chrono import IClock
from holobot.sdk.identification import IHoloflakeProvider
from holobot.sdk.ioc.decorators import injectable
from .iuser_item_manager import IUserItemManager

THandler = Callable[[int, int, Any], Awaitable[tuple[GrantItemOutcome, UserItem]]]

TItem = TypeVar("TItem", bound=ItemBase)
TDisplayInfo = TypeVar("TDisplayInfo", bound=ItemDisplayInfoBase)
TDisplayInfoFactory = Callable[[TItem], Awaitable[TDisplayInfo]]

@injectable(IUserItemManager)
class UserItemManager(IUserItemManager):
    def __init__(
        self,
        background_repository: IUserProfileBackgroundRepository,
        badge_repository: IBadgeRepository,
        clock: IClock,
        currency_repository: ICurrencyRepository,
        holoflake_provider: IHoloflakeProvider,
        user_item_repository: IUserItemRepository
    ) -> None:
        super().__init__()
        self.__background_repository = background_repository
        self.__badge_repository = badge_repository
        self.__clock = clock
        self.__currency_repository = currency_repository
        self.__holoflake_provider = holoflake_provider
        self.__user_item_repository = user_item_repository
        self.__quest_reward_handlers: dict[type, THandler] = {
            CurrencyQuestReward: self.__grant_currency_reward,
            BadgeQuestReward: self.__grant_badge_reward,
            BackgroundQuestReward: self.__grant_background_reward
        }
        self.__display_info_factories: dict[type, TDisplayInfoFactory[Any, Any]] = {
            CurrencyItem: self.__get_currency_display_info,
            BadgeItem: self.__get_badge_display_info,
            BackgroundItem: self.__get_background_display_info
        }

    async def grant_item(
        self,
        server_id: int,
        user_id: int,
        item: ItemBase
    ) -> tuple[GrantItemOutcome, UserItem]:
        if item.count <= 0:
            raise ValueError(f"Item has a count of {item.count}, but it must be a positive value.")

        if isinstance(item, CurrencyItem):
            return await self.__grant_currency(server_id, user_id, item.currency_id, item.count)
        if isinstance(item, BadgeItem):
            return await self.__grant_badge(server_id, user_id, item.badge_id)
        if isinstance(item, BackgroundItem):
            return await self.__grant_background(server_id, user_id, item.background_id)

        user_item = self.__create_user_item(server_id, user_id, item)

        await self.__user_item_repository.add(user_item)

        return (GrantItemOutcome.GRANTED, user_item)

    def try_grant_quest_reward(
        self,
        server_id: int,
        user_id: int,
        quest_reward: QuestRewardBase
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        if quest_reward.count <= 0:
            raise ValueError(
                f"Quest reward has a count of {quest_reward.count},"
                " but it must be a positive value."
            )

        if not (factory := self.__quest_reward_handlers.get(type(quest_reward))):
            raise ValueError(f"Unknown quest reward type '{type(quest_reward)}'.")

        return factory(server_id, user_id, quest_reward)

    def get_item_display_info(
        self,
        item: ItemBase
    ) -> Awaitable[ItemDisplayInfoBase]:
        if not (factory := self.__display_info_factories.get(type(item))):
            raise ValueError(f"Unknown item type '{type(item)}'.")

        return factory(item)

    def __grant_currency_reward(
        self,
        server_id: int,
        user_id: int,
        quest_reward: CurrencyQuestReward
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        return self.__grant_currency(
            server_id,
            user_id,
            quest_reward.currency_id,
            quest_reward.count
        )

    async def __grant_currency(
        self,
        server_id: int,
        user_id: int,
        currency_id: int,
        count: int
    ) -> tuple[GrantItemOutcome, UserItem]:
        user_item = await self.__user_item_repository.get_wallet(
            user_id,
            server_id,
            currency_id
        )
        if user_item:
            if not isinstance(user_item.item, CurrencyItem):
                raise InvalidItemTypeException(user_id, server_id, currency_id)

            user_item.item.count += count
            await self.__user_item_repository.update(user_item)
            return (GrantItemOutcome.GRANTED, user_item)

        user_item = self.__create_user_item(
            server_id,
            user_id,
            CurrencyItem(
                count=count,
                currency_id=currency_id
            )
        )

        await self.__user_item_repository.add(user_item)

        return (GrantItemOutcome.GRANTED, user_item)

    def __grant_badge_reward(
        self,
        server_id: int,
        user_id: int,
        quest_reward: BadgeQuestReward
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        return self.__grant_badge(
            server_id,
            user_id,
            quest_reward.badge_id
        )

    async def __grant_badge(
        self,
        server_id: int,
        user_id: int,
        badge_id: BadgeId
    ) -> tuple[GrantItemOutcome, UserItem]:
        user_item = await self.__user_item_repository.get_badge(
            server_id,
            user_id,
            badge_id.badge_id
        )
        if user_item:
            return (GrantItemOutcome.GRANTED_ALREADY, user_item)

        user_item = self.__create_user_item(
            server_id,
            user_id,
            BadgeItem(
                count=1,
                badge_id=badge_id,
                unlocked_at=self.__clock.now_utc()
            )
        )

        await self.__user_item_repository.add(user_item)

        return (GrantItemOutcome.GRANTED, user_item)

    def __grant_background_reward(
        self,
        server_id: int,
        user_id: int,
        quest_reward: BackgroundQuestReward
    ) -> Awaitable[tuple[GrantItemOutcome, UserItem]]:
        return self.__grant_background(
            server_id,
            user_id,
            quest_reward.background_id
        )

    async def __grant_background(
        self,
        server_id: int,
        user_id: int,
        background_id: int
    ) -> tuple[GrantItemOutcome, UserItem]:
        user_item = await self.__user_item_repository.get_background(user_id, background_id)
        if user_item:
            return (GrantItemOutcome.GRANTED_ALREADY, user_item)

        user_item = self.__create_user_item(
            server_id,
            user_id,
            BackgroundItem(
                count=1,
                background_id=background_id
            )
        )

        await self.__user_item_repository.add(user_item)

        return (GrantItemOutcome.GRANTED, user_item)

    def __create_user_item(
        self,
        server_id: int,
        user_id: int,
        item: ItemBase
    ) -> UserItem:
        return UserItem(
            identifier=UserItemId(
                server_id=server_id,
                user_id=user_id,
                serial_id=self.__holoflake_provider.get_next_id()
            ),
            item=item
        )

    def __get_currency_display_info(
        self,
        item: CurrencyItem
    ) -> Awaitable[CurrencyDisplayInfo]:
        return self.__currency_repository.get_display_info(item.currency_id)

    def __get_badge_display_info(
        self,
        item: BadgeItem
    ) -> Awaitable[BadgeDisplayInfo]:
        return self.__badge_repository.get_display_info(item.badge_id)

    def __get_background_display_info(
        self,
        item: BackgroundItem
    ) -> Awaitable[BackgroundDisplayInfo]:
        return self.__background_repository.get_display_info(item.background_id)
