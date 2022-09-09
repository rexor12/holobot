from typing import Protocol, TypeVar

TValue = TypeVar("TValue")

class IConfigurator(Protocol):
    def get(self, section: str, parameter: str, default_value: TValue) -> TValue:
        ...
