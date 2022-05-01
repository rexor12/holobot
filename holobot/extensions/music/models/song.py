from dataclasses import dataclass, field
from datetime import datetime
from holobot.discord.sdk.audio import IAudioSource
from typing import Optional

@dataclass
class Song:
    url: str
    queueing_user_id: str
    audio_source: IAudioSource
    queued_at: datetime = field(default_factory=lambda: datetime.utcnow())
    started_at: Optional[datetime] = None
