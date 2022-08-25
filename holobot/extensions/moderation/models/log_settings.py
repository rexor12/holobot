from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(kw_only=True)
class LogSettings:
    identifier: int = -1
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    server_id: str
    channel_id: str
