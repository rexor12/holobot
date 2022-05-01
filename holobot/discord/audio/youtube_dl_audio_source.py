from asyncio.events import AbstractEventLoop, get_event_loop
from datetime import timedelta
from discord.opus import Encoder
from discord.player import FFmpegPCMAudio, PCMVolumeTransformer
from holobot.discord.sdk.audio import IAudioSource
from typing import Any, List, Optional, Tuple
from yt_dlp import YoutubeDL

FFMPEG_PARAMETERS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

class YouTubeDlAudioSource(PCMVolumeTransformer, IAudioSource):
    def __init__(self, source, *, data, volume=1.0):
        super().__init__(source, volume)
        self.__title: str = data.get("title", "Unknown song")
        self.__duration: Optional[timedelta] = timedelta(seconds=data.get("duration")) if data.get("duration", None) else None
        self.__url: Optional[str] = data.get("url", None)
        self.__played_milliseconds: int = 0
        
    @property
    def title(self) -> str:
        return self.__title
    
    @property
    def duration(self) -> Optional[timedelta]:
        return self.__duration
    
    @property
    def url(self) -> Optional[str]:
        return self.__url

    @property
    def played_milliseconds(self) -> int:
        return self.__played_milliseconds
    
    def read(self) -> bytes:
        read_bytes = super().read()
        self.__played_milliseconds += Encoder.FRAME_LENGTH
        return read_bytes

    @staticmethod
    async def from_url(extractor: YoutubeDL, url: str, *, loop: Optional[AbstractEventLoop] = None, stream: bool = False) -> 'Tuple[YouTubeDlAudioSource, ...]':
        loop = loop or get_event_loop()
        data: Any = await loop.run_in_executor(None, lambda: extractor.extract_info(url, download=not stream))
        # TODO Handle playlist items.
        playlist_items = [data["entries"][0]] if "entries" in data else [data]
        audio_sources: List[YouTubeDlAudioSource] = []
        for playlist_item in playlist_items:
            filename = playlist_item["url"] if stream else extractor.prepare_filename(playlist_item)
            audio_sources.append(YouTubeDlAudioSource(
                FFmpegPCMAudio(
                    executable="C:\\Program Files\\ffmpeg\\ffmpeg.exe", # TODO Configuration, defaulting to "ffmpeg" simply.
                    source=filename,
                    **FFMPEG_PARAMETERS),
                data=playlist_item))
        return tuple(audio_sources)
