from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.repositories import Record

@dataclass
class TransactionRecord(Record[int]):
    id: int
    created_at: datetime
    owner_id: str
    target_id: str
    amount: int
    message: str | None
    is_finalized: bool
    is_completed: bool
