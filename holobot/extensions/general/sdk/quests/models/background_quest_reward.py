from dataclasses import dataclass

from .quest_reward_base import QuestRewardBase

@dataclass(kw_only=True)
class BackgroundQuestReward(QuestRewardBase):
    background_id: int
    name: str
