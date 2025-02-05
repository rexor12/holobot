from dataclasses import dataclass

from holobot.sdk.database.entities import AggregateRoot
from .valentine2025_rating_id import Valentine2025RatingId

@dataclass(kw_only=True)
class Valentine2025Rating(AggregateRoot[Valentine2025RatingId]):
    score1: int
    score2: int
    score3: int
    score4: int
    score5: int
    score6: int
    message: str | None
    is_deleted: bool = False
