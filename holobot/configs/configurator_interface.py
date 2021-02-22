from typing import TypeVar

T = TypeVar("T")

class ConfiguratorInterface:
    def get(self, section: str, parameter: str, default_value: T) -> T:
        raise NotImplementedError
