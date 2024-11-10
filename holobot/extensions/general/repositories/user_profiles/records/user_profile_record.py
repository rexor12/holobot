from dataclasses import dataclass

from holobot.sdk.database.entities import PrimaryKey, Record
from holobot.sdk.database.repositories import manually_generated_key

@manually_generated_key
@dataclass
class UserProfileRecord(Record):
    id: PrimaryKey[int]
    reputation_points: int
    background_image_code: str | None
    show_badges: bool
    badge_sid1: int | None = None
    badge_id1: int | None = None
    badge_sid2: int | None = None
    badge_id2: int | None = None
    badge_sid3: int | None = None
    badge_id3: int | None = None
    badge_sid4: int | None = None
    badge_id4: int | None = None
    badge_sid5: int | None = None
    badge_id5: int | None = None
    badge_sid6: int | None = None
    badge_id6: int | None = None
    badge_sid7: int | None = None
    badge_id7: int | None = None
    badge_sid8: int | None = None
    badge_id8: int | None = None
