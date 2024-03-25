from dataclasses import dataclass

from .quest_reward_base import QuestRewardBase

@dataclass(kw_only=True)
class CurrencyQuestReward(QuestRewardBase):
    currency_id: int
    emoji_id: int
    emoji_name: str
