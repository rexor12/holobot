from typing import Any, TypeVar

_JSON_TYPE_HIERARCHY_ROOT_ATTR: str = "_holo_json_type_hierarchy_root"

T = TypeVar("T")

def json_type_hierarchy_root():
    def wrapper(target: type[T]):
        setattr(target, _JSON_TYPE_HIERARCHY_ROOT_ATTR, True)
        return target
    return wrapper
