from .song import Song
from dataclasses import dataclass, field
from datetime import datetime
from holobot.sdk.concurrency import AsyncProducerConsumerQueue
from typing import Optional

@dataclass
class MusicContext:
    server_id: str
    channel_id: str
    initiating_user_id: str
    initiated_at: datetime = field(default_factory=lambda: datetime.utcnow())
    current_song: Optional[Song] = None
    queue: AsyncProducerConsumerQueue[Song] = field(default_factory=lambda: AsyncProducerConsumerQueue())
    last_song_finished_at: datetime = field(default_factory=lambda: datetime.utcnow())
