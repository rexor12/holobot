from dataclasses import dataclass
from holobot.sdk.reactive.models import EventBase

@dataclass
class UserLeftAudioChannelEvent(EventBase):
    server_id: str
    channel_id: str
    user_id: str
