import random
from collections.abc import Iterable

from holobot.extensions.general.sdk import IQuestRewardFactory
from holobot.extensions.general.sdk.currencies.data_providers import ICurrencyDataProvider
from holobot.extensions.general.sdk.quests.models import CurrencyQuestReward, QuestRewardBase
from holobot.extensions.mudada.configs import MudadaOptions
from holobot.extensions.mudada.models.easter_reward import EasterReward
from holobot.extensions.mudada.repositories import IEasterRewardRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.datetime_utils import utcnow

_CURRENCY_CODE = "EASTER2024"
_REWARD_BY_TIERS = {
    0: 11000,
    1: 12000,
    2: 13000,
    3: 14000,
    4: 15000
}

@injectable(IQuestRewardFactory)
class EasterQuestRewardFactory(IQuestRewardFactory):
    @property
    def relevant_server_ids(self) -> tuple[int, ...]:
        return (self.__options.value.MudadaServerId,)

    @property
    def relevant_quest_codes(self) -> tuple[str, ...]:
        return ("MUDADA_EASTER_2024",)

    def __init__(
        self,
        currency_data_provider: ICurrencyDataProvider,
        easter_reward_repository: IEasterRewardRepository,
        options: IOptions[MudadaOptions],
    ) -> None:
        self.__currency_data_provider = currency_data_provider
        self.__easter_reward_repository = easter_reward_repository
        self.__options = options

    async def create_quest_rewards(
        self,
        quest_code: str,
        server_id: int,
        user_id: int
    ) -> Iterable[QuestRewardBase]:
        currency = await self.__currency_data_provider.get_currency_by_code(server_id, _CURRENCY_CODE)
        if not currency:
            return ()

        easter_reward = await self.__easter_reward_repository.get(user_id)
        if not easter_reward:
            reward_tier, reward_amount, is_pity = EasterQuestRewardFactory.__generate_reward(-1)
            easter_reward = EasterReward(
                identifier=user_id,
                last_update_at=utcnow(),
                last_reward_tier=reward_tier
            )
            await self.__easter_reward_repository.add(easter_reward)
        else:
            reward_tier, reward_amount, is_pity = EasterQuestRewardFactory.__generate_reward(
                easter_reward.last_reward_tier
            )
            easter_reward.last_reward_tier = reward_tier
            await self.__easter_reward_repository.update(easter_reward)

        return (CurrencyQuestReward(
            currency_id=currency.identifier,
            count=reward_amount,
            emoji_id=currency.emoji_id,
            emoji_name=currency.emoji_name,
            extension_data={
                "tier": reward_tier,
                "is_pity": is_pity
            }
        ),)

    @staticmethod
    def __generate_reward(last_reward_tier: int) -> tuple[int, int, bool]:
        reward_tier_count = len(_REWARD_BY_TIERS)
        if last_reward_tier == 0:
            return (reward_tier_count - 1, _REWARD_BY_TIERS[reward_tier_count - 1], True)

        new_reward_tier = random.randint(0, reward_tier_count - 1)

        return (new_reward_tier, _REWARD_BY_TIERS[new_reward_tier], False)
