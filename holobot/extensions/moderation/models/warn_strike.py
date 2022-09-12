from dataclasses import dataclass, field
from datetime import datetime

from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class WarnStrike:
    identifier: int = -1
    created_at: datetime = field(default_factory=utcnow)
    server_id: str
    user_id: str
    reason: str
    warner_id: str
