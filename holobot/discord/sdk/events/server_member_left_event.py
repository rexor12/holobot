from dataclasses import dataclass

from holobot.sdk.reactive.models import EventBase

@dataclass(kw_only=True, frozen=True)
class ServerMemberLeftEvent(EventBase):
    server_id: int
    user_id: int
