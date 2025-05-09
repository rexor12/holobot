from dataclasses import dataclass, field
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot
from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class LogSettings(AggregateRoot[int]):
    identifier: int = -1
    modified_at: datetime = field(default_factory=utcnow)
    server_id: int
    channel_id: int
