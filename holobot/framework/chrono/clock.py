import time
from datetime import datetime, timezone

from holobot.sdk.chrono import IClock
from holobot.sdk.ioc.decorators import injectable

@injectable(IClock)
class Clock(IClock):
    def now_utc(self) -> datetime:
        return datetime.now(timezone.utc)

    def time_utc(self) -> float:
        return time.time()
