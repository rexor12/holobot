from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Record

@dataclass(kw_only=True)
class LogSettingsRecord(Record[int]):
    id: int
    modified_at: datetime
    server_id: str
    channel_id: str
