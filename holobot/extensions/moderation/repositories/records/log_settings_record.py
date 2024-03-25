from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class LogSettingsRecord(Record):
    id: PrimaryKey[int]
    modified_at: datetime
    server_id: str
    channel_id: str
