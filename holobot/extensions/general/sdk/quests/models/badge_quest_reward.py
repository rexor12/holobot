from dataclasses import dataclass

from holobot.extensions.general.sdk.badges.models import BadgeId
from .quest_reward_base import QuestRewardBase

@dataclass(kw_only=True)
class BadgeQuestReward(QuestRewardBase):
    badge_id: BadgeId
    name: str
