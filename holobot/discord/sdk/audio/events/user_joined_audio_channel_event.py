from dataclasses import dataclass
from holobot.sdk.reactive.models import EventBase

@dataclass
class UserJoinedAudioChannelEvent(EventBase):
    server_id: str
    channel_id: str
    user_id: str
