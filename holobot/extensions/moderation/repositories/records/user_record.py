from dataclasses import dataclass
from datetime import datetime

from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.sdk.database.repositories import Entity

@dataclass(kw_only=True)
class UserRecord(Entity[int]):
    id: int
    created_at: datetime
    server_id: str
    user_id: str
    permissions: ModeratorPermission
