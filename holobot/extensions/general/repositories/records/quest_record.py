from dataclasses import dataclass
from datetime import datetime

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass(kw_only=True)
class QuestRecord(Record):
    server_id: PrimaryKey[str]
    user_id: PrimaryKey[str]
    quest_proto_code: PrimaryKey[str]
    completed_at: datetime | None
    objective_count_1: int
    objective_count_2: int
    repeat_count: int | None
