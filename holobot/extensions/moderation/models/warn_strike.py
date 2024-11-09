from dataclasses import dataclass, field
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class WarnStrike(AggregateRoot[int]):
    identifier: int = -1
    created_at: datetime = field(default_factory=utcnow)
    server_id: int
    user_id: int
    reason: str
    warner_id: int
