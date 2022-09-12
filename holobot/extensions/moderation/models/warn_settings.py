from dataclasses import dataclass, field
from datetime import datetime, timedelta

from holobot.sdk.utils import utcnow

@dataclass(kw_only=True)
class WarnSettings:
    identifier: int = -1
    modified_at: datetime = field(default_factory=utcnow)
    server_id: str
    decay_threshold: timedelta | None = None
    auto_mute_after: int = 0
    auto_mute_duration: timedelta | None = None
    auto_kick_after: int = 0
    auto_ban_after: int = 0

    @property
    def has_auto_features(self) -> bool:
        return (
            self.auto_mute_after > 0
            or self.auto_kick_after > 0
            or self.auto_ban_after > 0
        )
