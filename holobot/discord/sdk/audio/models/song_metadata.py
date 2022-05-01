from dataclasses import dataclass
from datetime import timedelta

@dataclass
class SongMetadata:
    url: str
    title: str
    duration: timedelta
