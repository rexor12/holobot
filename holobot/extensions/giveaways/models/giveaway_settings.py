from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(kw_only=True)
class GiveawaySettings:
    identifier: int = 0
    modified_at: datetime = datetime.now(timezone.utc)
    server_id: str
    announce_channel_id: str | None = None
