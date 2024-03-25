from dataclasses import dataclass
from datetime import datetime, timedelta

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass
class ChannelTimerRecord(Record):
    id: PrimaryKey[int]
    user_id: str
    server_id: str
    channel_id: str
    base_time: datetime
    countdown_interval: timedelta
    name_template: str | None
    expiry_name_template: str | None
