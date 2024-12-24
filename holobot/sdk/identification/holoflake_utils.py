from datetime import datetime, timedelta, timezone
from typing import Final

# 2024-11-15 00:00:00 UTC+00:00
HOLO_EPOCH_MS: Final[int] = 1_731_628_800_000
HOLO_EPOCH: Final[timedelta] = timedelta(milliseconds=HOLO_EPOCH_MS)

def holo_epoch_offset_to_datetime(offset: int) -> datetime:
    return datetime.fromtimestamp(offset / 1000, timezone.utc) + HOLO_EPOCH

def datetime_to_holo_epoch_offset(timestamp: datetime) -> int:
    return int((timestamp - HOLO_EPOCH).timestamp() * 1000)

def timestamp_to_holo_epoch_offset(timestamp: float) -> int:
    return int(timestamp * 1000) - HOLO_EPOCH_MS
