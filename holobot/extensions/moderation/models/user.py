from dataclasses import dataclass, field
from datetime import datetime

from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.sdk.database import AggregateRoot
from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class User(AggregateRoot[int]):
    identifier: int = -1
    created_at: datetime = field(default_factory=utcnow)
    server_id: str
    user_id: str
    permissions: ModeratorPermission = ModeratorPermission.NONE
