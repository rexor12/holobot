from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass
class CurrencyRecord(Record):
    id: PrimaryKey[int]
    created_at: datetime
    created_by: int
    server_id: int | None
    name: str
    description: str | None
    emoji_id: int
    emoji_name: str
    is_tradable: bool
