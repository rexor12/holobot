from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class Valentine2025RatingRecord(Record):
    source_user_id: PrimaryKey[int]
    target_user_id: PrimaryKey[int]
    score1: int
    score2: int
    score3: int
    score4: int
    score5: int
    score6: int
    message: str | None
    is_deleted: bool
