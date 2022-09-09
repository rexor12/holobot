from dataclasses import dataclass, field
from datetime import datetime

from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class TodoItem:
    identifier: int = -1
    user_id: str
    created_at: datetime = field(default_factory=utcnow)
    message: str
