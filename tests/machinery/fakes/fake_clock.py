from datetime import datetime, timezone

from holobot.sdk.chrono import IClock

class FakeClock(IClock):
    def __init__(self) -> None:
        super().__init__()
        self.__now_utc = datetime(2024, 11, 11, 15, 0, 0, tzinfo=timezone.utc)

    def now_utc(self) -> datetime:
        return self.__now_utc

    def time_utc(self) -> float:
        return self.__now_utc.timestamp()

    def set_now(self, now_utc: datetime) -> None:
        if now_utc.tzinfo != timezone.utc:
            raise ValueError("Time zone must be UTC.")

        self.__now_utc = now_utc
