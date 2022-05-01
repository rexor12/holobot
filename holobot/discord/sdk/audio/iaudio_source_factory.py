from .iaudio_source import IAudioSource
from .models import SongMetadata
from typing import Tuple

class IAudioSourceFactory:
    async def create_from_url(self, url: str) -> Tuple[IAudioSource, ...]:
        raise NotImplementedError

    async def search(self, keywords: str, max_count: int = 10) -> Tuple[SongMetadata, ...]:
        raise NotImplementedError
