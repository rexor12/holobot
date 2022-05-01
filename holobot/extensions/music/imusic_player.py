from .enums import QueueMode
from .models import Song
from holobot.discord.sdk.audio.models import SongMetadata
from holobot.discord.sdk.models import PagedResults
from typing import Optional, Tuple

MAX_SEARCH_RESULTS: int = 5

class IMusicPlayer:
    async def join_channel(self, server_id: str, channel_id: str, initiating_user_id: str) -> None:
        raise NotImplementedError

    async def stop_playback(self, server_id: str, clear_queue: bool, leave_channel: bool) -> None:
        raise NotImplementedError

    async def queue_songs(self, server_id: str, user_id: str, url: str, mode: QueueMode = QueueMode.AS_LAST) -> Tuple[Song, ...]:
        raise NotImplementedError
    
    async def skip_song(self, server_id: str) -> None:
        raise NotImplementedError

    async def search_songs(self, keywords: str, max_count: int = MAX_SEARCH_RESULTS) -> Tuple[SongMetadata, ...]:
        raise NotImplementedError

    async def get_channel_id(self, server_id: str) -> Optional[str]:
        raise NotImplementedError
    
    async def get_currently_playing_song(self, server_id: str) -> Optional[Song]:
        raise NotImplementedError
    
    async def get_queued_songs(self, server_id: str, page_index: int, page_size: int = 10) -> PagedResults[Song]:
        raise NotImplementedError
