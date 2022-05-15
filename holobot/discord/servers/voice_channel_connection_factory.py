from discord import VoiceClient
from discord.channel import VoiceChannel
from holobot.discord.audio import AudioClient
from holobot.discord.sdk.audio import IAudioClient
from holobot.discord.sdk.servers import IVoiceChannelConnectionFactory
from holobot.discord.utils import get_guild_channel
from holobot.sdk.ioc.decorators import injectable

@injectable(IVoiceChannelConnectionFactory)
class VoiceChannelConnectionFactory(IVoiceChannelConnectionFactory):
    async def create(self, server_id: str, channel_id: str) -> IAudioClient:
        channel = get_guild_channel(server_id, channel_id)
        if not isinstance(channel, VoiceChannel):
            raise Exception("Not a voice channel.")

        voice_client = await channel.connect(cls=VoiceClient)
        if not isinstance(voice_client, VoiceClient):
            raise Exception(f"discord.py returned the unexpected voice client type '{type(voice_client)}'.")

        return AudioClient(voice_client)
