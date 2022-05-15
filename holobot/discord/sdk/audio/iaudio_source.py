from datetime import timedelta
from typing import Optional

class IAudioSource:
    @property
    def title(self) -> str:
        raise NotImplementedError
    
    @property
    def duration(self) -> Optional[timedelta]:
        raise NotImplementedError
    
    @property
    def url(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def played_milliseconds(self) -> int:
        raise NotImplementedError
