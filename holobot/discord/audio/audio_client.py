from .youtube_dl_audio_source import YouTubeDlAudioSource
from discord import VoiceClient
from holobot.discord.sdk.audio import IAudioClient, IAudioSource
from holobot.sdk.concurrency import TaskCompletionSource

class AudioClient(IAudioClient):
    def __init__(self, voice_client: VoiceClient) -> None:
        super().__init__()
        self.__voice_client: VoiceClient = voice_client

    async def close(self) -> None:
        await self.__voice_client.disconnect()
    
    async def play(self, source: IAudioSource) -> None:
        if not isinstance(source, YouTubeDlAudioSource):
            raise TypeError(f"The audio source of type '{type(source)}' is not supported.")
        
        task_completion_source: TaskCompletionSource[bool] = TaskCompletionSource()
        self.__voice_client.play(source, after=lambda e: task_completion_source.set_result(True))
        await task_completion_source.task()
    
    async def stop(self) -> None:
        self.__voice_client.stop()
