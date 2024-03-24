from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class EasterRewardRecord(Record):
    id: PrimaryKey[str]
    last_update_at: datetime
    last_reward_tier: int
