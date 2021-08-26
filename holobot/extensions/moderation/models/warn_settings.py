from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

@dataclass
class WarnSettings:
    auto_mute_after: int = 0
    auto_mute_duration: Optional[timedelta] = None
    auto_kick_after: int = 0
    auto_ban_after: int = 0

    @property
    def has_auto_features(self) -> bool:
        return (
            self.auto_mute_after > 0
            or self.auto_kick_after > 0
            or self.auto_ban_after > 0
        )