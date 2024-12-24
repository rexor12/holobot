from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class UserProfileBackgroundRecord(Record):
    id: PrimaryKey[int]
    created_at: datetime
    code: str
    name: str
