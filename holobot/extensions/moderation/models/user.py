from dataclasses import dataclass, field
from datetime import datetime, timezone

from holobot.extensions.moderation.enums import ModeratorPermission

@dataclass(kw_only=True)
class User:
    identifier: int = -1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    server_id: str
    user_id: str
    permissions: ModeratorPermission = ModeratorPermission.NONE
