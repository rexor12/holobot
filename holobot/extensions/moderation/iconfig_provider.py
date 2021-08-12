from datetime import timedelta
from holobot.sdk.math import Range

class IConfigProvider:
    def get_reason_length_range(self) -> Range[int]:
        raise NotImplementedError

    def get_decay_threshold_range(self) -> Range[timedelta]:
        raise NotImplementedError
