from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class BadgeRecord(Record):
    server_id: PrimaryKey[str]
    badge_id: PrimaryKey[int]
    created_by: str
    created_at: datetime
    name: str
    description: str | None
    emoji_name: str
    emoji_id: int
