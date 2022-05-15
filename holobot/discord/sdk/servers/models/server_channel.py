from dataclasses import dataclass
from holobot.discord.sdk.models import Channel

@dataclass
class ServerChannel(Channel):
    server_id: str
    name: str
