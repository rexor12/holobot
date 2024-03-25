from dataclasses import dataclass
from datetime import datetime, timedelta

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class WarnSettingsRecord(Record):
    id: PrimaryKey[int]
    modified_at: datetime
    server_id: str
    decay_threshold: timedelta | None
    auto_mute_after: int
    auto_mute_duration: timedelta | None
    auto_kick_after: int
    auto_ban_after: int
