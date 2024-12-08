from datetime import datetime
from typing import Protocol

class IClock(Protocol):
    def now_utc(self) -> datetime:
        ...

    def time_utc(self) -> float:
        ...
