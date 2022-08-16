from dataclasses import dataclass

from holobot.discord.sdk.models import Channel

@dataclass
class ServerChannel(Channel):
    name: str
