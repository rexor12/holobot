from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Record

@dataclass(kw_only=True)
class TodoItemRecord(Record[int]):
    id: int
    user_id: str
    created_at: datetime
    message: str
