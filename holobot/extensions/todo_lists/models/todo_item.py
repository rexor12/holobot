from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(kw_only=True)
class TodoItem:
    identifier: int = -1
    user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str
