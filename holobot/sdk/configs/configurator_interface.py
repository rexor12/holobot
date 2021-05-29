from typing import TypeVar

TValue = TypeVar("TValue")

class ConfiguratorInterface:
    def get(self, section: str, parameter: str, default_value: TValue) -> TValue:
        raise NotImplementedError
