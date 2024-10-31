import random
from collections.abc import Iterable

from holobot.extensions.general.sdk import IQuestRewardFactory
from holobot.extensions.general.sdk.currencies.data_providers import ICurrencyDataProvider
from holobot.extensions.general.sdk.quests.models import CurrencyQuestReward, QuestRewardBase
from holobot.extensions.mudada.configs import MudadaOptions
from holobot.extensions.mudada.constants import MUDADA_SERVER_ID
from holobot.extensions.mudada.models.halloween_reward import HalloweenReward
from holobot.extensions.mudada.repositories import IHalloweenRewardRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.datetime_utils import utcnow

_REWARD_BY_TIERS = {
    0: 11000,
    1: 12000,
    2: 13000,
    3: 14000,
    4: 15000
}

@injectable(IQuestRewardFactory)
class Halloween2024QuestRewardFactory(IQuestRewardFactory):
    @property
    def relevant_server_ids(self) -> tuple[str, ...]:
        return (MUDADA_SERVER_ID,)

    @property
    def relevant_quest_codes(self) -> tuple[str, ...]:
        return ("MUDADA_HALLOWEEN_2024",)

    def __init__(
        self,
        currency_data_provider: ICurrencyDataProvider,
        halloween_reward_repository: IHalloweenRewardRepository,
        options: IOptions[MudadaOptions]
    ) -> None:
        self.__currency_data_provider = currency_data_provider
        self.__halloween_reward_repository = halloween_reward_repository
        self.__options = options

    async def create_quest_rewards(
        self,
        quest_code: str,
        server_id: str,
        user_id: str
    ) -> Iterable[QuestRewardBase]:
        currency = await self.__currency_data_provider.get_currency_by_code(
            server_id,
            self.__options.value.MuderaCurrencyCode
        )
        if not currency:
            return ()

        halloween_reward = await self.__halloween_reward_repository.get(user_id)
        if not halloween_reward:
            reward_tier, reward_amount, is_pity, is_tricked = Halloween2024QuestRewardFactory.__generate_reward(-1, False)
            halloween_reward = HalloweenReward(
                identifier=user_id,
                last_update_at=utcnow(),
                last_reward_tier=reward_tier,
                is_tricked=is_tricked
            )
            await self.__halloween_reward_repository.add(halloween_reward)
        else:
            reward_tier, reward_amount, is_pity, is_tricked = Halloween2024QuestRewardFactory.__generate_reward(
                halloween_reward.last_reward_tier,
                halloween_reward.is_tricked
            )
            halloween_reward.last_reward_tier = reward_tier
            halloween_reward.is_tricked = is_tricked
            await self.__halloween_reward_repository.update(halloween_reward)

        return (CurrencyQuestReward(
            currency_id=currency.identifier,
            count=reward_amount,
            emoji_id=currency.emoji_id,
            emoji_name=currency.emoji_name,
            extension_data={
                "tier": reward_tier,
                "is_pity": is_pity,
                "is_tricked": is_tricked
            }
        ),)

    @staticmethod
    def __generate_reward(last_reward_tier: int, is_tricked: bool) -> tuple[int, int, bool, bool]:
        if not is_tricked:
            reward_multiplier = 1
            is_tricked = random.random() < 0.1
            if is_tricked:
                return (last_reward_tier, 0, False, True)
        else:
            reward_multiplier = 2

        reward_tier_count = len(_REWARD_BY_TIERS)
        if last_reward_tier == 0:
            return (
                reward_tier_count - 1,
                _REWARD_BY_TIERS[reward_tier_count - 1] * reward_multiplier,
                True,
                False
            )

        new_reward_tier = random.randint(0, reward_tier_count - 1)

        return (
            new_reward_tier,
            _REWARD_BY_TIERS[new_reward_tier] * reward_multiplier,
            False,
            False
        )
