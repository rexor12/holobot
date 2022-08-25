from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class LogSettingsRecord(Entity[int]):
    id: int
    modified_at: datetime
    server_id: str
    channel_id: str
