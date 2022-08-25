from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class TodoItemRecord(Entity[int]):
    id: int
    user_id: str
    created_at: datetime
    message: str
