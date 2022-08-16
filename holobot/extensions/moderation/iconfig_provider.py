from datetime import timedelta

from holobot.sdk.math import Range

class IConfigProvider:
    def get_reason_length_range(self) -> Range[int]:
        raise NotImplementedError

    def get_decay_threshold_range(self) -> Range[timedelta]:
        raise NotImplementedError

    def get_warn_cleanup_interval(self) -> timedelta:
        raise NotImplementedError

    def get_warn_cleanup_delay(self) -> timedelta:
        raise NotImplementedError

    def get_mute_duration_range(self) -> Range[timedelta]:
        raise NotImplementedError

    def get_mute_cleanup_interval(self) -> timedelta:
        raise NotImplementedError

    def get_mute_cleanup_delay(self) -> timedelta:
        raise NotImplementedError
