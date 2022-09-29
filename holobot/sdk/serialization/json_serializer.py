import json
from collections.abc import Callable
from dataclasses import is_dataclass
from datetime import datetime
from typing import Any, TypeVar

from dateutil.parser import isoparse

from holobot.sdk.utils.dataclass_utils import get_parameter_infos

T = TypeVar("T")

PRIMITIVE_DESERIALIZERS: dict[type, Callable[[Any], Any]] = {
    str: lambda obj: obj,
    bool: lambda obj: obj,
    int: lambda obj: int(obj) if obj is not None else 0,
    float: lambda obj: float(obj) if obj is not None else 0.0,
    datetime: lambda obj: isoparse(obj) if obj else None
}

def deserialize(object_type: type[T], json_data: str | dict) -> T | None:
    json_object = json.loads(json_data) if isinstance(json_data, str) else json_data
    return __deserialize_instance(object_type, json_object)

def __deserialize_instance(object_type: type[T], json_object: Any) -> T | None:
    if json_object is None:
        return None

    if (deserializer := PRIMITIVE_DESERIALIZERS.get(object_type)) is not None:
        return deserializer(json_object)

    if not is_dataclass(object_type):
        raise ValueError((
            f"Cannot deserialize type '{object_type}'."
            " It must be either a primitive type or a dataclass."
        ))

    parameter_infos = get_parameter_infos(object_type)
    arguments: dict[str, Any] = {}
    for parameter_info in parameter_infos:
        if parameter_info.collection_constructor is not None:
            argument_items = [
                __deserialize_instance(parameter_info.object_type, item)
                for item in (json_object.get(parameter_info.name) or [])
            ]
            arguments[parameter_info.name] = parameter_info.collection_constructor(argument_items)
        else:
            argument = __deserialize_instance(parameter_info.object_type, json_object.get(parameter_info.name))
            if argument is None and not parameter_info.allows_none:
                if parameter_info.default_value:
                    argument = parameter_info.default_value
                elif parameter_info.default_factory:
                    argument = parameter_info.default_factory()
                else:
                    raise ValueError(
                        f"Deserialized None for attribute '{parameter_info.name}'"
                        " which doesn't accept it as a valid value."
                    )
            arguments[parameter_info.name] = argument

    return object_type(**arguments)
