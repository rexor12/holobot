from dataclasses import dataclass
from datetime import datetime, timedelta

from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class WarnSettingsRecord(Entity[int]):
    id: int
    modified_at: datetime
    server_id: str
    decay_threshold: timedelta | None
    auto_mute_after: int
    auto_mute_duration: timedelta | None
    auto_kick_after: int
    auto_ban_after: int
