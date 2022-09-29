from datetime import timedelta

from holobot.extensions.moderation.models import ModerationOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.math import Range
from .iconfig_provider import IConfigProvider

@injectable(IConfigProvider)
class ConfigProvider(IConfigProvider):
    def __init__(self, options: IOptions[ModerationOptions]) -> None:
        super().__init__()
        self.__options = options

    def get_reason_length_range(self) -> Range[int]:
        options = self.__options.value
        return Range(options.ReasonLengthMin, options.ReasonLengthMax)

    def get_decay_threshold_range(self) -> Range[timedelta]:
        options = self.__options.value
        return Range(
            timedelta(seconds=options.DecayThresholdMin),
            timedelta(seconds=options.DecayThresholdMax)
        )

    def get_warn_cleanup_interval(self) -> timedelta:
        return timedelta(seconds=self.__options.value.WarnCleanupInterval)

    def get_warn_cleanup_delay(self) -> timedelta:
        return timedelta(seconds=self.__options.value.WarnCleanupInterval)

    def get_mute_duration_range(self) -> Range[timedelta]:
        options = self.__options.value
        return Range(
            timedelta(seconds=options.MuteDurationMin),
            timedelta(seconds=options.MuteDurationMax)
        )

    def get_mute_cleanup_interval(self) -> timedelta:
        return timedelta(seconds=self.__options.value.MuteCleanupInterval)

    def get_mute_cleanup_delay(self) -> timedelta:
        return timedelta(seconds=self.__options.value.MuteCleanupDelay)
