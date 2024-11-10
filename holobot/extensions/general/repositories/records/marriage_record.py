from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass
class MarriageRecord(Record):
    id: PrimaryKey[int]
    server_id: int
    user_id1: int
    user_id2: int
    married_at: datetime
    level: int
    last_level_up_at: datetime | None
    exp_points: int
    last_activity_at: datetime | None
    activity_tier_reset_at: datetime
    activity_tier: int
    hug_count: int
    kiss_count: int
    pat_count: int
    poke_count: int
    lick_count: int
    bite_count: int
    handhold_count: int
    cuddle_count: int
    match_bonus: int
