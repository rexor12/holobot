import json
from collections.abc import Callable
from dataclasses import is_dataclass
from datetime import datetime
from typing import Any, TypeVar, get_args, get_origin

from dateutil.parser import isoparse

from holobot.sdk.utils.dataclass_utils import (
    DictionaryTypeDescriptor, ObjectTypeDescriptor, get_parameter_infos
)

T = TypeVar("T")

_DESERIALIZERS: dict[type, Callable[[type, Any], Any]] = {
    str: lambda _, obj: obj,
    bool: lambda _, obj: obj if isinstance(obj, bool) else str(obj).lower() == "true",
    int: lambda _, obj: int(obj) if obj is not None else 0,
    float: lambda _, obj: float(obj) if obj is not None else 0.0,
    datetime: lambda _, obj: isoparse(obj) if obj else None,
    dict: lambda t, obj: __deserialize_dict(t, obj)
}

def deserialize(object_type: type[T], json_data: str | dict) -> T | None:
    json_object = json.loads(json_data) if isinstance(json_data, str) else json_data
    return __deserialize_instance(object_type, json_object)

def __deserialize_instance(object_type: type[T], json_object: Any) -> T | None:
    if json_object is None:
        return None

    origin = get_origin(object_type)
    if deserializer := _DESERIALIZERS.get(origin or object_type, None):
        return deserializer(object_type, json_object)

    if is_dataclass(object_type):
        return __deserialize_dataclass(object_type, json_object)

    raise TypeError(f"Cannot deserialize unknown type {object_type}.")

def __deserialize_dict(dict_type: type, json_object: Any) -> dict[Any, Any]:
    parameters = get_args(dict_type)
    return {
        key: __deserialize_instance(parameters[1], value)
        for key, value in (json_object or {}).items()
    }

def __deserialize_dataclass(object_type: type[T], json_object: Any) -> T | None:
    parameter_infos = get_parameter_infos(object_type)
    arguments: dict[str, Any] = {}
    for parameter_info in parameter_infos:
        if parameter_info.collection_constructor is dict:
            if not isinstance(parameter_info.object_type, DictionaryTypeDescriptor):
                raise TypeError(
                    "Expected the collection parameter's descriptor to be"
                    f" an DictionaryTypeDescriptor, but got {parameter_info.object_type}."
                )

            argument_items = {
                key: __deserialize_instance(parameter_info.object_type.value_type, value)
                for key, value in (json_object.get(parameter_info.name) or {}).items()
            }
            arguments[parameter_info.name] = argument_items
        elif parameter_info.collection_constructor is not None:
            if not isinstance(parameter_info.object_type, ObjectTypeDescriptor):
                raise TypeError(
                    "Expected the collection parameter's descriptor to be"
                    f" an ObjectTypeDescriptor, but got {parameter_info.object_type}."
                )

            argument_items = [
                __deserialize_instance(parameter_info.object_type.value, item)
                for item in (json_object.get(parameter_info.name) or [])
            ]
            arguments[parameter_info.name] = parameter_info.collection_constructor(argument_items)
        else:
            if not isinstance(parameter_info.object_type, ObjectTypeDescriptor):
                raise TypeError(
                    "Expected the non-collection parameter's descriptor to be"
                    f" an ObjectTypeDescriptor, but got {parameter_info.object_type}."
                )

            argument = __deserialize_instance(parameter_info.object_type.value, json_object.get(parameter_info.name))
            if argument is None and not parameter_info.allows_none:
                if parameter_info.default_value:
                    argument = parameter_info.default_value
                elif parameter_info.default_factory:
                    argument = parameter_info.default_factory()
                else:
                    raise TypeError(
                        f"Deserialized None for attribute '{parameter_info.name}'"
                        " which doesn't accept it as a valid value."
                    )
            arguments[parameter_info.name] = argument

    return object_type(**arguments)
