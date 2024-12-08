from typing import Generic, TypeVar

from holobot.sdk.configs import IOptions

TOptions = TypeVar("TOptions")

class FakeOptionsProvider(IOptions, Generic[TOptions]):
    @property
    def value(self) -> TOptions:
        return self.__options

    def __init__(self, options: TOptions) -> None:
        super().__init__()
        self.__options = options
