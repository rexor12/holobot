from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class WarnStrikeRecord(Entity[int]):
    id: int
    created_at: datetime
    server_id: str
    user_id: str
    reason: str
    warner_id: str
