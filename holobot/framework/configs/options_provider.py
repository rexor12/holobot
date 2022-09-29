from typing import Generic

from holobot.sdk import Lazy
from holobot.sdk.configs import IConfigurator
from holobot.sdk.configs.ioptions import IOptions, TOptions
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.serialization import deserialize

@injectable(IOptions)
class OptionsProvider(Generic[TOptions], IOptions[TOptions]):
    @property
    def value(self) -> TOptions:
        return self.__value_lazy.value

    @property
    def generic_type_argument(self) -> type[TOptions]:
        # The implementation is provided by the IoC framework.
        raise NotImplementedError

    def __init__(
        self,
        configurator: IConfigurator
    ) -> None:
        super().__init__()
        self.__configurator = configurator
        self.__value_lazy = Lazy[TOptions](self.__deserialize_options)

    def __deserialize_options(self) -> TOptions:
        container_section = self.__configurator.effective_config.get(
            self.generic_type_argument.section_name,
            {}
        )
        options_section = container_section.get(self.generic_type_argument.__name__)
        if options_section and (instance := deserialize(self.generic_type_argument, options_section)):
            return instance
        return self.generic_type_argument()
