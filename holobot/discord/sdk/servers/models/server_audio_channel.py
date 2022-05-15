from .server_channel import ServerChannel
from dataclasses import dataclass
from holobot.discord.sdk.models import AudioChannel

@dataclass
class ServerAudioChannel(AudioChannel, ServerChannel):
    pass
