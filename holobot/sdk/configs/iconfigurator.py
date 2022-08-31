from typing import TypeVar

TValue = TypeVar("TValue")

class IConfigurator:
    def get(self, section: str, parameter: str, default_value: TValue) -> TValue:
        raise NotImplementedError
