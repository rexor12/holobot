from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class UserReward(AggregateRoot[int]):
    reward_amount: int
