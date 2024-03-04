from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class WarnStrikeRecord(Record):
    id: PrimaryKey[int]
    created_at: datetime
    server_id: str
    user_id: str
    reason: str
    warner_id: str
