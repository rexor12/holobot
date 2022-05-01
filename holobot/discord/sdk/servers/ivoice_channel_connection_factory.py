from holobot.discord.sdk.audio import IAudioClient

class IVoiceChannelConnectionFactory:
    async def create(self, server_id: str, channel_id: str) -> IAudioClient:
        raise NotImplementedError
