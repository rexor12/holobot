from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.sdk.database.entities import PrimaryKey, Record

@dataclass(kw_only=True)
class UserRecord(Record):
    id: PrimaryKey[int]
    created_at: datetime
    server_id: int
    user_id: int
    permissions: ModeratorPermission
