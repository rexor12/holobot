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

    # TODO Move this to IAudioClient (see implementation).
    # Because an audio source is but a source, so it shouldn't maintain a playback state.
    @property
    def played_milliseconds(self) -> int:
        raise NotImplementedError
