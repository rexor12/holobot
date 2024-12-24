from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import AggregateRoot

@dataclass(kw_only=True)
class UserProfileBackground(AggregateRoot[int]):
    created_at: datetime
    code: str
    name: str
