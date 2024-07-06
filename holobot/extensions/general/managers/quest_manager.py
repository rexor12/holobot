from collections.abc import Awaitable, Iterable, Sequence
from datetime import timedelta

from holobot.extensions.general.enums import QuestResetType
from holobot.extensions.general.models import Quest, QuestProto, Wallet
from holobot.extensions.general.repositories import (
    ICurrencyRepository, IQuestProtoRepository, IQuestRepository, IWalletRepository
)
from holobot.extensions.general.sdk import IQuestRewardFactory
from holobot.extensions.general.sdk.quests.dtos import QuestRewardDescriptor
from holobot.extensions.general.sdk.quests.enums import QuestStatus
from holobot.extensions.general.sdk.quests.exceptions import (
    InvalidQuestException, QuestNotStartedException, QuestOnCooldownException,
    QuestStillInProgressException, QuestUnavailableException
)
from holobot.extensions.general.sdk.quests.managers import IQuestManager
from holobot.extensions.general.sdk.quests.models import (
    CurrencyQuestReward, IQuest, QuestId, QuestProtoId, QuestRewardBase
)
from holobot.extensions.general.sdk.wallets.models import WalletId
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.datetime_utils import get_last_day_of_week, today_midnight_utc, utcnow
from holobot.sdk.utils.iterable_utils import multi_to_dict, of_type

@injectable(IQuestManager)
class QuestManager(IQuestManager):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        logger_factory: ILoggerFactory,
        quest_proto_repository: IQuestProtoRepository,
        quest_repository: IQuestRepository,
        quest_reward_factories: tuple[IQuestRewardFactory, ...],
        wallet_repository: IWalletRepository
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__logger = logger_factory.create(QuestManager)
        self.__quest_proto_repository = quest_proto_repository
        self.__quest_repository = quest_repository
        self.__wallet_repository = wallet_repository
        # TODO IQuestRewardFactory per server, not just code!
        self.__quest_reward_factories = multi_to_dict(
            quest_reward_factories,
            lambda i: i.relevant_quest_codes
        )

    async def start_quest(
        self,
        server_id: str,
        user_id: str,
        quest_proto_id: QuestProtoId
    ) -> IQuest:
        quest_proto = await self.__quest_proto_repository.get(quest_proto_id)
        if not quest_proto:
            raise InvalidQuestException(quest_proto_id, "This quest prototype doesn't exist.")

        if (quest := await self.__get_quest(server_id, user_id, quest_proto_id)):
            if not quest.completed_at:
                return quest

        can_start_quest, cooldown = QuestManager.__can_start_quest(quest_proto, quest)
        if not can_start_quest:
            if cooldown is not None:
                raise QuestOnCooldownException(quest_proto_id, cooldown)
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
        server_id: str,
        user_id: str,
        quest_proto_id: QuestProtoId
    ) -> QuestRewardDescriptor:
        quest_proto = await self.__quest_proto_repository.get(quest_proto_id)
        if not quest_proto:
            raise InvalidQuestException(quest_proto_id, "This quest prototype doesn't exist.")

        if not (quest := await self.__get_quest(server_id, user_id, quest_proto_id)):
            raise QuestNotStartedException(quest_proto_id)

        if not QuestManager.__are_objectives_complete(quest_proto, quest):
            raise QuestStillInProgressException(
                quest_proto_id,
                "Not all quest objectives have been completed yet."
            )

        # TODO Add character XP, SP and items.
        quest.completed_at = utcnow()
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
        server_id: str,
        user_id: str,
        quest_proto_id: QuestProtoId
    ) -> QuestStatus:
        quest_proto = await self.__quest_proto_repository.get(quest_proto_id)
        if not quest_proto:
            return QuestStatus.MISSING

        if (quest := await self.__get_quest(server_id, user_id, quest_proto_id)):
            if not quest.completed_at:
                return QuestStatus.IN_PROGRESS

        can_start_quest, _ = QuestManager.__can_start_quest(quest_proto, quest)

        return QuestStatus.AVAILABLE if can_start_quest else QuestStatus.UNAVAILABLE

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

    @staticmethod
    def __can_start_quest(
        quest_proto: QuestProto,
        quest: Quest | None
    ) -> tuple[bool, timedelta | None]:
        # The quest has never been started, yet.
        if not quest:
            return (True, None)

        # The quest is still in progress or the quest is non-repeatable.
        if not quest.completed_at or quest_proto.reset_type is QuestResetType.NONE:
            return (False, None)

        match quest_proto.reset_type:
            case QuestResetType.INTERVAL:
                if quest_proto.reset_time is None:
                    return (False, None)

                elapsed_time = utcnow() - quest.completed_at
                return (
                    elapsed_time >= quest_proto.reset_time,
                    quest_proto.reset_time - elapsed_time
                )
            case QuestResetType.DAILY_AT:
                if quest_proto.reset_time is None:
                    return (False, None)

                last_reset_time = today_midnight_utc() + quest_proto.reset_time
                next_reset_time = last_reset_time + timedelta(days=1)
                return (
                    quest.completed_at < last_reset_time,
                    next_reset_time - utcnow()
                )
            case QuestResetType.WEEKLY_AT:
                if quest_proto.reset_time is None:
                    return (False, None)

                last_reset_time = get_last_day_of_week(0) + quest_proto.reset_time
                next_reset_time = last_reset_time + timedelta(days=1)
                return (
                    quest.completed_at < last_reset_time,
                    next_reset_time - utcnow()
                )
            case QuestResetType.MONTHLY_AT:
                if quest_proto.reset_time is None:
                    return (False, None)

                last_reset_time = today_midnight_utc().replace(day=0) + quest_proto.reset_time
                return (
                    quest.completed_at < last_reset_time,
                    None # TODO Figure out how many days are in a month.
                )
            case QuestResetType.ON_COMPLETION:
                return (True, None)
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
        server_id: str,
        user_id: str,
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
        server_id: str,
        user_id: str,
        quest_proto: QuestProto
    ) -> Sequence[QuestRewardBase]:
        # TODO Grant non-currency items as well.
        granted_rewards = list[QuestRewardBase](await self.__get_granted_currencies(quest_proto))
        # TODO IQuestRewardFactory per server, not just code!
        if factory := self.__quest_reward_factories.get(quest_proto.identifier.code):
            for quest_reward in await factory.create_quest_rewards(quest_proto.identifier.code, server_id, user_id):
                granted_rewards.append(quest_reward)

        await self.__grant_currencies(server_id, user_id, of_type(granted_rewards, CurrencyQuestReward))

        return granted_rewards

    async def __grant_currencies(
        self,
        server_id: str,
        user_id: str,
        currencies: Iterable[CurrencyQuestReward]
    ) -> None:
        for currency in currencies:
            wallet_id = WalletId(
                user_id=user_id,
                currency_id=currency.currency_id,
                server_id=server_id
            )
            wallet = await self.__wallet_repository.get(wallet_id)
            if wallet:
                wallet.amount += currency.count
                await self.__wallet_repository.update(wallet)
            else:
                wallet = Wallet(
                    identifier=wallet_id,
                    amount=currency.count
                )
                await self.__wallet_repository.add(wallet)

    async def __get_granted_currencies(
        self,
        quest_proto: QuestProto
    ) -> Sequence[CurrencyQuestReward]:
        granted_currencies = list[CurrencyQuestReward]()
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

            granted_currencies.append(CurrencyQuestReward(
                currency_id=currency_id,
                emoji_id=currency.emoji_id,
                emoji_name=currency.emoji_name,
                count=currency_count
            ))

        return granted_currencies
