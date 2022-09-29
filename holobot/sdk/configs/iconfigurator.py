from typing import Any, Protocol, TypeVar

TValue = TypeVar("TValue", str, int, bool, list[str])

class IConfigurator(Protocol):
    @property
    def effective_config(self) -> dict[str, Any]:
        ...

    def get_parameter(
        self,
        section_name: str | tuple[str, ...],
        parameter_name: str,
        default_value: TValue
    ) -> TValue:
        ...
