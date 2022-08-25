from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(kw_only=True)
class WarnStrike:
    identifier: int = -1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    server_id: str
    user_id: str
    reason: str
    warner_id: str
