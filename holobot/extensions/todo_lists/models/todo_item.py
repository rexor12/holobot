from dataclasses import dataclass, field
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class TodoItem(AggregateRoot[int]):
    identifier: int = -1
    user_id: int
    created_at: datetime = field(default_factory=utcnow)
    message: str
