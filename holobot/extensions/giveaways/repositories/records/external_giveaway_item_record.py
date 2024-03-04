from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass
class ExternalGiveawayItemRecord(Record):
    id: PrimaryKey[int]
    created_at: datetime
    start_time: datetime | None
    end_time: datetime
    source_name: str
    item_type: str
    url: str
    preview_url: str | None
    title: str
