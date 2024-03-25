from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class TodoItemRecord(Record):
    id: PrimaryKey[int]
    user_id: str
    created_at: datetime
    message: str
