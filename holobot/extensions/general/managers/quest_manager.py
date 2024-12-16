from collections.abc import AsyncGenerator, Awaitable, Sequence
from datetime import timedelta

from holobot.extensions.general.enums import QuestResetType
from holobot.extensions.general.models import Quest, QuestProto
from holobot.extensions.general.models.items import BadgeItem, CurrencyItem, UserItem
from holobot.extensions.general.repositories import (
    IBadgeRepository, ICurrencyRepository, IQuestProtoRepository, IQuestRepository,
    IUserItemRepository
)
from holobot.extensions.general.sdk import IQuestRewardFactory
from holobot.extensions.general.sdk.badges.models import BadgeId
from holobot.extensions.general.sdk.items.exceptions import InvalidItemTypeException
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.extensions.general.sdk.quests.dtos import QuestRewardDescriptor
from holobot.extensions.general.sdk.quests.enums import QuestStatus
from holobot.extensions.general.sdk.quests.exceptions import (
    InvalidQuestException, QuestCompletedAlreadyException, QuestNotStartedException,
    QuestOnCooldownException, QuestStillInProgressException, QuestUnavailableException
)
from holobot.extensions.general.sdk.quests.managers import IQuestManager
from holobot.extensions.general.sdk.quests.models import (
    BackgroundQuestReward, BadgeQuestReward, CurrencyQuestReward, IQuest, QuestId, QuestProtoId,
    QuestRewardBase
)
from holobot.sdk.chrono import IClock
from holobot.sdk.identification import IHoloflakeProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.datetime_utils import get_last_day_of_week, today_midnight_utc
from holobot.sdk.utils.iterable_utils import multi_to_dict

@injectable(IQuestManager)
class QuestManager(IQuestManager):
    def __init__(
        self,
        badge_repository: IBadgeRepository,
        clock: IClock,
        currency_repository: ICurrencyRepository,
        holoflake_provider: IHoloflakeProvider,
        logger_factory: ILoggerFactory,
        quest_proto_repository: IQuestProtoRepository,
        quest_repository: IQuestRepository,
        quest_reward_factories: tuple[IQuestRewardFactory, ...],
        user_item_repository: IUserItemRepository
    ) -> None:
        super().__init__()
        self.__badge_repository = badge_repository
        self.__clock = clock
        self.__currency_repository = currency_repository
        self.__holoflake_provider = holoflake_provider
        self.__logger = logger_factory.create(QuestManager)
        self.__quest_proto_repository = quest_proto_repository
        self.__quest_repository = quest_repository
        self.__user_item_repository = user_item_repository
        # TODO IQuestRewardFactory per server, not just code!
        self.__quest_reward_factories = multi_to_dict(
            quest_reward_factories,
            lambda i: i.relevant_quest_codes
        )

    async def start_quest(
        self,
        server_id: int,
        user_id: int,
        quest_proto_id: QuestProtoId
    ) -> IQuest:
        quest_proto = await self.__quest_proto_repository.get(quest_proto_id)
        if not quest_proto:
            raise InvalidQuestException(quest_proto_id, "This quest prototype doesn't exist.")

        if (quest := await self.__get_quest(server_id, user_id, quest_proto_id)):
            if not quest.completed_at:
                return quest

        availability, cooldown = self.__get_quest_status(quest_proto, quest)
        if availability == QuestStatus.ON_COOLDOWN:
            # cooldown must be non-None if the quest is on cooldown.
            assert cooldown
            raise QuestOnCooldownException(quest_proto_id, cooldown)
        elif availability == QuestStatus.COMPLETED:
            raise QuestCompletedAlreadyException(quest_proto_id)
        elif availability != QuestStatus.AVAILABLE:
            raise QuestUnavailableException(
                quest_proto_id,
                "The quest cannot be started at this time."
            )

        if quest:
            quest.completed_at = None
            await self.__quest_repository.update(quest)
            return quest

        quest = Quest(
            identifier=QuestId(
                server_id=quest_proto_id.server_id,
                quest_proto_code=quest_proto_id.code,
                user_id=user_id
            )
        )
        await self.__quest_repository.add(quest)

        return quest

    async def complete_quest(
        self,
        server_id: int,
        user_id: int,
        quest_proto_id: QuestProtoId
    ) -> QuestRewardDescriptor:
        quest_proto = await self.__quest_proto_repository.get(quest_proto_id)
        if not quest_proto:
            raise InvalidQuestException(quest_proto_id, "This quest prototype doesn't exist.")

        now = self.__clock.now_utc()
        if (
            (quest_proto.valid_from is not None and now < quest_proto.valid_from)
            or (quest_proto.valid_to is not None and now > quest_proto.valid_to)
        ):
            raise QuestUnavailableException(quest_proto_id, "This quest has expired already or is not available yet.")

        if not (quest := await self.__get_quest(server_id, user_id, quest_proto_id)):
            raise QuestNotStartedException(quest_proto_id)

        if not QuestManager.__are_objectives_complete(quest_proto, quest):
            raise QuestStillInProgressException(
                quest_proto_id,
                "Not all quest objectives have been completed yet."
            )

        # TODO Add character XP, SP and items.
        quest.completed_at = now
        quest.repeat_count = quest.repeat_count + 1 if quest.repeat_count is not None else 1
        await self.__quest_repository.update(quest)
        granted_items = await self.__grant_rewards(quest.identifier.server_id, user_id, quest_proto)

        return QuestRewardDescriptor(
            quest_proto_id=quest_proto_id,
            title=quest_proto.title,
            note=quest_proto.note,
            completion_text=quest_proto.completion_text,
            granted_items=granted_items,
            granted_xp=quest_proto.reward_xp,
            granted_sp=quest_proto.reward_sp
        )

    async def get_quest_status(
        self,
        server_id: int,
        user_id: int,
        quest_proto_id: QuestProtoId
    ) -> QuestStatus:
        quest_proto = await self.__quest_proto_repository.get(quest_proto_id)
        if not quest_proto:
            return QuestStatus.MISSING

        quest = await self.__get_quest(server_id, user_id, quest_proto_id)
        status, _ = self.__get_quest_status(quest_proto, quest)

        return status

    @staticmethod
    def __are_objectives_complete(
        quest_proto: QuestProto,
        quest: Quest | None
    ) -> bool:
        if not quest:
            return False

        return (
            quest.objective_count_1 >= quest_proto.objective_count_1
            and quest.objective_count_2 >= quest_proto.objective_count_2
        )

    def __get_quest_status(
        self,
        quest_proto: QuestProto,
        quest: Quest | None
    ) -> tuple[QuestStatus, timedelta | None]:
        # The quest has never been started, yet.
        if not quest:
            return (QuestStatus.AVAILABLE, None)

        if not quest.completed_at:
            return (QuestStatus.IN_PROGRESS, None)

        if quest_proto.reset_type is QuestResetType.NONE:
            return (QuestStatus.COMPLETED, None)

        # The (repeatable) quest cannot be completed any more times by the user.
        if (
            quest_proto.max_repeats is not None
            and quest.repeat_count is not None
            and quest.repeat_count >= quest_proto.max_repeats
        ):
            return (QuestStatus.COMPLETED, None)

        # The quest has expired already or is not available yet.
        now = self.__clock.now_utc()
        if (
            (quest_proto.valid_from is not None and now < quest_proto.valid_from)
            or (quest_proto.valid_to is not None and now > quest_proto.valid_to)
        ):
            return (QuestStatus.UNAVAILABLE, None)

        match quest_proto.reset_type:
            case QuestResetType.INTERVAL:
                if quest_proto.reset_time is None:
                    return (QuestStatus.UNAVAILABLE, None)

                elapsed_time = self.__clock.now_utc() - quest.completed_at
                return (
                    (
                        QuestStatus.AVAILABLE
                        if elapsed_time >= quest_proto.reset_time
                        else QuestStatus.ON_COOLDOWN
                    ),
                    quest_proto.reset_time - elapsed_time
                )
            case QuestResetType.DAILY_AT:
                if quest_proto.reset_time is None:
                    return (QuestStatus.UNAVAILABLE, None)

                last_reset_time = today_midnight_utc() + quest_proto.reset_time
                next_reset_time = last_reset_time + timedelta(days=1)
                return (
                    (
                        QuestStatus.AVAILABLE
                        if quest.completed_at < last_reset_time
                        else QuestStatus.ON_COOLDOWN
                    ),
                    next_reset_time - self.__clock.now_utc()
                )
            case QuestResetType.WEEKLY_AT:
                if quest_proto.reset_time is None:
                    return (QuestStatus.UNAVAILABLE, None)

                last_reset_time = get_last_day_of_week(0) + quest_proto.reset_time
                next_reset_time = last_reset_time + timedelta(days=1)
                return (
                    (
                        QuestStatus.AVAILABLE
                        if quest.completed_at < last_reset_time
                        else QuestStatus.ON_COOLDOWN
                    ),
                    next_reset_time - self.__clock.now_utc()
                )
            case QuestResetType.MONTHLY_AT:
                if quest_proto.reset_time is None:
                    return (QuestStatus.UNAVAILABLE, None)

                last_reset_time = today_midnight_utc().replace(day=0) + quest_proto.reset_time
                return (
                    (
                        QuestStatus.AVAILABLE
                        if quest.completed_at < last_reset_time
                        else QuestStatus.ON_COOLDOWN
                    ),
                    None # TODO Figure out how many days are in a month.
                )
            case QuestResetType.ON_COMPLETION:
                return (QuestStatus.AVAILABLE, None)
            case QuestResetType.CUSTOM:
                # TODO Implement custom quest reset handling.
                raise NotImplementedError
            case _:
                raise ValueError(
                    f"The quest prototype with ID '{quest_proto.identifier}'"
                    f" has an invalid reset type '{quest_proto.reset_type}'."
                )

    def __get_quest(
        self,
        server_id: int,
        user_id: int,
        quest_proto_id: QuestProtoId
    ) -> Awaitable[Quest | None]:
        return self.__quest_repository.get(
            QuestId(
                user_id=user_id,
                server_id=server_id,
                quest_proto_code=quest_proto_id.code
            )
        )

    async def __grant_rewards(
        self,
        server_id: int,
        user_id: int,
        quest_proto: QuestProto
    ) -> Sequence[QuestRewardBase]:
        granted_rewards = list[QuestRewardBase]()
        async for quest_reward in self.__create_quest_rewards(quest_proto, server_id, user_id):
            if await self.__try_grant_reward(
                quest_reward,
                server_id,
                user_id,
                quest_proto.identifier
            ):
                granted_rewards.append(quest_reward)

        return granted_rewards

    async def __create_quest_rewards(
        self,
        quest_proto: QuestProto,
        server_id: int,
        user_id: int
    ) -> AsyncGenerator[QuestRewardBase]:
        async for granted_currency in self.__create_currency_rewards(quest_proto):
            yield granted_currency

        async for granted_badge in self.__create_badge_rewards(quest_proto):
            yield granted_badge

        if factory := self.__quest_reward_factories.get(quest_proto.identifier.code):
            for quest_reward in await factory.create_quest_rewards(
                quest_proto.identifier.code,
                server_id,
                user_id
            ):
                yield quest_reward

    async def __create_currency_rewards(
        self,
        quest_proto: QuestProto
    ) -> AsyncGenerator[CurrencyQuestReward]:
        rewards = (
            (quest_proto.reward_currency_id_1, quest_proto.reward_currency_count_1),
            (quest_proto.reward_currency_id_2, quest_proto.reward_currency_count_2)
        )
        for currency_id, currency_count in rewards:
            if currency_id is None:
                continue

            currency = await self.__currency_repository.get(currency_id)
            if not currency:
                continue

            yield CurrencyQuestReward(
                currency_id=currency_id,
                emoji_id=currency.emoji_id,
                emoji_name=currency.emoji_name,
                count=currency_count
            )

    async def __create_badge_rewards(
        self,
        quest_proto: QuestProto
    ) -> AsyncGenerator[BadgeQuestReward]:
        rewards = (
            (quest_proto.reward_badge_sid_1, quest_proto.reward_badge_id_1),
        )
        for server_id, badge_id in rewards:
            if server_id is None or badge_id is None:
                continue

            typed_badge_id = BadgeId(
                server_id=server_id,
                badge_id=badge_id
            )
            badge_name = await self.__badge_repository.get_badge_name(typed_badge_id)
            if not badge_name:
                continue

            yield BadgeQuestReward(
                count=1,
                badge_id=typed_badge_id,
                name=badge_name
            )

    async def __try_grant_reward(
        self,
        quest_reward: QuestRewardBase,
        server_id: int,
        user_id: int,
        quest_proto_id: QuestProtoId
    ) -> bool:
        if quest_reward.count <= 0:
            return False
        if isinstance(quest_reward, CurrencyQuestReward):
            return await self.__try_grant_currency(quest_reward, server_id, user_id)
        if isinstance(quest_reward, BadgeQuestReward):
            return await self.__try_grant_badge(quest_reward, user_id)
        if isinstance(quest_reward, BackgroundQuestReward):
            return await self.__try_grant_background(quest_reward, user_id)

        self.__logger.warning(
            "Failed to grant an unknown quest item",
            server_id=server_id,
            user_id=user_id,
            quest_reward_type=type(quest_reward).__name__,
            quest_proto_id=str(quest_proto_id)
        )

        return False

    async def __try_grant_currency(
        self,
        quest_reward: CurrencyQuestReward,
        server_id: int,
        user_id: int
    ) -> bool:
        user_item = await self.__user_item_repository.get_wallet(
            user_id,
            server_id,
            quest_reward.currency_id
        )
        if user_item:
            if not isinstance(user_item.item, CurrencyItem):
                raise InvalidItemTypeException(user_id, server_id, quest_reward.currency_id)

            user_item.item.count += quest_reward.count
            await self.__user_item_repository.update(user_item)
        else:
            await self.__user_item_repository.add(UserItem(
                identifier=UserItemId(
                    server_id=server_id,
                    user_id=user_id,
                    serial_id=self.__holoflake_provider.get_next_id()
                ),
                item=CurrencyItem(
                    count=quest_reward.count,
                    currency_id=quest_reward.currency_id
                )
            ))

        return True

    async def __try_grant_badge(
        self,
        quest_reward: BadgeQuestReward,
        user_id: int
    ) -> bool:
        has_badge_already = await self.__user_item_repository.badge_exists(
            quest_reward.badge_id.server_id,
            user_id,
            quest_reward.badge_id.badge_id
        )
        if has_badge_already:
            # Already acquired
            return True

        user_item = UserItem(
            identifier=UserItemId(
                server_id=quest_reward.badge_id.server_id,
                user_id=user_id,
                serial_id=self.__holoflake_provider.get_next_id()
            ),
            item=BadgeItem(
                count=1,
                badge_id=quest_reward.badge_id,
                unlocked_at=self.__clock.now_utc()
            )
        )

        await self.__user_item_repository.add(user_item)

        return True

    async def __try_grant_background(
        self,
        quest_reward: BackgroundQuestReward,
        user_id: int
    ) -> bool:
        raise NotImplementedError
