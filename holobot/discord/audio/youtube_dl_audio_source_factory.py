from .youtube_dl_audio_source import YouTubeDlAudioSource
from datetime import timedelta
from holobot.discord.sdk.audio import IAudioSource, IAudioSourceFactory
from holobot.discord.sdk.audio.models import SongMetadata
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from typing import List, Tuple
from yt_dlp import YoutubeDL

import asyncio

YOUTUBE_DL_PARAMETERS = {
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "format": "bestaudio/best",
    "ignoreerrors": False,
    "noplaylist": True,
    "quiet": True,
    "logtostderr": False,
    "no_warnings": True,
    "subtitleslangs": False,
    "writesubtitles": False,
    "age_limit": 27,
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "verbose": False
}

downloader = YoutubeDL(YOUTUBE_DL_PARAMETERS)

@injectable(IAudioSourceFactory)
class YoutubeDlAudioSourceFactory(IAudioSourceFactory):
    def __init__(self, configurator: ConfiguratorInterface) -> None:
        super().__init__()
        self.__ffmpeg_path: str = configurator.get("Music", "FfmpegPath", "ffmpeg")

    async def create_from_url(self, url: str) -> Tuple[IAudioSource, ...]:
        return await YouTubeDlAudioSource.from_url(downloader, url, self.__ffmpeg_path, stream=True)

    async def search(self, keywords: str, max_count: int = 10) -> Tuple[SongMetadata, ...]:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: downloader.extract_info(f"ytsearch{max_count}:{keywords}", download=False))
        if not data:
            return ()

        metadatas: List[SongMetadata] = []
        items = data["entries"] if "entries" in data else [data]
        for item in items:
            if ("webpage_url" not in item
                or "title" not in item
                or "duration" not in item):
                continue
            metadatas.append(SongMetadata(
                url=item["webpage_url"],
                title=item["title"],
                duration=timedelta(seconds=item["duration"])
            ))
        return tuple(metadatas)
