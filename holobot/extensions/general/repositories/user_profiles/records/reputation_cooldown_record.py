from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class ReputationCooldownRecord(Record):
    id: PrimaryKey[int]
    last_target_user_id: int
    last_rep_at: datetime
