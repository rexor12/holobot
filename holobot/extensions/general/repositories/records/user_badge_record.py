from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class UserBadgeRecord(Record):
    user_id: PrimaryKey[int]
    server_id: PrimaryKey[int]
    badge_id: PrimaryKey[int]
    unlocked_at: datetime
