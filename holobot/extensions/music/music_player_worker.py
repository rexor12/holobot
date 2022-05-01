from .models import MusicContext
from datetime import datetime
from holobot.discord.sdk.audio import IAudioClient
from holobot.sdk.concurrency import CancellationToken
from typing import Any, Awaitable, Callable, Generator

import asyncio

class MusicPlayerWorker(Awaitable[None]):
    def __init__(self,
                 music_context: MusicContext,
                 client: IAudioClient,
                 token: CancellationToken,
                 on_queue_empty: Callable[['MusicPlayerWorker'], Awaitable[None]]) -> None:
        self.__music_context: MusicContext = music_context
        self.__client: IAudioClient = client
        self.__token: CancellationToken = token
        self.__on_queue_empty: Callable[['MusicPlayerWorker'], Awaitable[None]] = on_queue_empty
        self.__consumer: Awaitable[None] = asyncio.create_task(self.__consume_songs())

    def __await__(self) -> Generator[Any, None, None]:
        return self.__consumer.__await__()
    
    @property
    def music_context(self) -> MusicContext:
        return self.__music_context
    
    @property
    def audio_client(self) -> IAudioClient:
        return self.__client
    
    async def stop_playback(self) -> None:
        await self.__client.stop()
        
    async def skip_song(self) -> None:
        await self.__client.stop()
        self.__music_context.current_song = None
    
    def shutdown(self) -> None:
        self.__token.cancel()
    
    async def __consume_songs(self) -> None:
        await asyncio.sleep(0) # Yield
        while not self.__token.is_cancellation_requested:
            if self.__music_context.current_song is not None:
                await asyncio.sleep(3)
                continue

            song = await self.__music_context.queue.try_dequeue()
            if not song.has_value:
                await self.__on_queue_empty(self)
                if self.__token.is_cancellation_requested:
                    break
                await asyncio.sleep(3)
                continue

            self.__music_context.current_song = song.value
            song.value.started_at = datetime.utcnow()
            await self.__client.play(song.value.audio_source)
            self.__music_context.last_song_finished_at = datetime.utcnow()
            self.__music_context.current_song = None
