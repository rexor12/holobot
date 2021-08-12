from .iconfig_provider import IConfigProvider
from datetime import timedelta
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.math import Range

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
            timedelta(seconds=self.__configurator.get(SECTION_NAME, "DecayThresholdSecondsMin", 1800)),
            timedelta(seconds=self.__configurator.get(SECTION_NAME, "DecayThresholdSecondsMax", 2592000))
        )
