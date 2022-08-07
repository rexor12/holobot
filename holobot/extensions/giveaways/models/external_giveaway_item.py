from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ExternalGiveawayItem:
    identifier: int
    created_at: datetime
    start_time: Optional[datetime]
    end_time: datetime
    source_name: str
    item_type: str
    url: str
    preview_url: Optional[str]
    title: str
