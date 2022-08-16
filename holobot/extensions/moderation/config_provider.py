from datetime import timedelta

from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.math import Range
from .iconfig_provider import IConfigProvider

SECTION_NAME = "Moderation"

@injectable(IConfigProvider)
class ConfigProvider(IConfigProvider):
    def __init__(self, configurator: ConfiguratorInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator

    def get_reason_length_range(self) -> Range[int]:
        return Range(
            self.__configurator.get(SECTION_NAME, "ReasonLengthMin", 10),
            self.__configurator.get(SECTION_NAME, "ReasonLengthMax", 192)
        )

    def get_decay_threshold_range(self) -> Range[timedelta]:
        return Range(
            timedelta(seconds=self.__configurator.get(SECTION_NAME, "DecayThresholdMin", 1800)),
            timedelta(seconds=self.__configurator.get(SECTION_NAME, "DecayThresholdMax", 2592000))
        )

    def get_warn_cleanup_interval(self) -> timedelta:
        return timedelta(seconds=self.__configurator.get(SECTION_NAME, "WarnCleanupInterval", 3600))

    def get_warn_cleanup_delay(self) -> timedelta:
        return timedelta(seconds=self.__configurator.get(SECTION_NAME, "WarnCleanupDelay", 60))

    def get_mute_duration_range(self) -> Range[timedelta]:
        return Range(
            timedelta(seconds=self.__configurator.get(SECTION_NAME, "MuteDurationMin", 60)),
            timedelta(seconds=self.__configurator.get(SECTION_NAME, "MuteDurationMax", 2592000))
        )

    def get_mute_cleanup_interval(self) -> timedelta:
        return timedelta(seconds=self.__configurator.get(SECTION_NAME, "MuteCleanupInterval", 60))

    def get_mute_cleanup_delay(self) -> timedelta:
        return timedelta(seconds=self.__configurator.get(SECTION_NAME, "MuteCleanupDelay", 60))
