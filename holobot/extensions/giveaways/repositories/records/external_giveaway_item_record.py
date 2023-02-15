from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Record

@dataclass
class ExternalGiveawayItemRecord(Record[int]):
    id: int
    created_at: datetime
    start_time: datetime | None
    end_time: datetime
    source_name: str
    item_type: str
    url: str
    preview_url: str | None
    title: str
