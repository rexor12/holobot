from datetime import timedelta
from typing import Protocol

from holobot.sdk.math import Range

class IConfigProvider(Protocol):
    def get_reason_length_range(self) -> Range[int]:
        ...

    def get_decay_threshold_range(self) -> Range[timedelta]:
        ...

    def get_warn_cleanup_interval(self) -> timedelta:
        ...

    def get_warn_cleanup_delay(self) -> timedelta:
        ...

    def get_mute_duration_range(self) -> Range[timedelta]:
        ...

    def get_mute_cleanup_interval(self) -> timedelta:
        ...

    def get_mute_cleanup_delay(self) -> timedelta:
        ...
