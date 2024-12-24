from typing import Any, Protocol, TypeVar

T = TypeVar("T")

class IJsonSerializerInternal(Protocol):
    def _deserialize_dict(self, dict_type: type, obj: Any) -> dict[Any, Any]:
        ...

    def _deserialize_dataclass(self, object_type: type[T], obj: Any) -> T | None:
        ...

    def _deserialize_list(self, list_type: type, obj: Any) -> list[Any]:
        ...
