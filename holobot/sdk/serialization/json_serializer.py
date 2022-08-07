from dataclasses import _MISSING_TYPE, fields, is_dataclass
from datetime import datetime
from dateutil.parser import isoparse
from typing import (
    Any, Callable, Dict, NamedTuple, Optional,
    Sequence, Type, TypeVar, Union, get_args, get_type_hints
)

import json

T = TypeVar("T")

PRIMITIVE_DESERIALIZERS: Dict[Type[Any], Callable[[Any], Any]] = {
    str: lambda obj: obj,
    int: lambda obj: int(obj) if obj is not None else 0,
    float: lambda obj: float(obj) if obj is not None else 0.0,
    datetime: lambda obj: isoparse(obj) if obj else None
}

class ArgumentInfo(NamedTuple):
    name: str
    object_type: Type[Any]
    collection_constructor: Optional[Type[Any]]
    allows_none: bool
    default_value: Any
    default_factory: Optional[Callable[[], Any]]

def deserialize(object_type: Type[T], json_data: Union[str, dict]) -> Optional[T]:
    json_object = json.loads(json_data) if isinstance(json_data, str) else json_data
    return __deserialize_instance(object_type, json_object)

def __deserialize_instance(object_type: Type[T], json_object: Any) -> Optional[T]:
    if json_object is None:
        return None

    if (deserializer := PRIMITIVE_DESERIALIZERS.get(object_type, None)) is not None:
        return deserializer(json_object)

    if not is_dataclass(object_type):
        raise ValueError(f"Cannot deserialize type '{object_type}'. It must be either a primitive type or a dataclass.")

    argument_infos = __get_argument_infos(object_type)
    arguments: Dict[str, Any] = {}
    for argument_info in argument_infos:
        if argument_info.collection_constructor is not None:
            argument_items = [
                __deserialize_instance(argument_info.object_type, item)
                for item in (json_object.get(argument_info.name) or [])
            ]
            arguments[argument_info.name] = argument_info.collection_constructor(argument_items)
        else:
            argument = __deserialize_instance(argument_info.object_type, json_object.get(argument_info.name))
            if argument is None and not argument_info.allows_none:
                if argument_info.default_value:
                    argument = argument_info.default_value
                elif argument_info.default_factory:
                    argument = argument_info.default_factory()
                else: raise ValueError("Deserialized None where it wasn't allowed.")
            arguments[argument_info.name] = argument

    return object_type(**arguments)

def __get_argument_infos(object_type: Type[Any]) -> Sequence[ArgumentInfo]:
    initializer = getattr(object_type, "__init__", None)
    if not initializer:
        raise ValueError(f"Type '{object_type}' has no __init__ method.")

    # Need to explicitly load type hints for dataclasses.
    # See: https://stackoverflow.com/a/55938344
    resolved_type_hints = get_type_hints(initializer)

    return [
        __get_argument_info(
            field_info.name,
            resolved_type_hints[field_info.name],
            None if isinstance(field_info.default, _MISSING_TYPE) else field_info.default,
            None if isinstance(field_info.default_factory, _MISSING_TYPE) else field_info.default_factory
        ) for field_info in fields(object_type)
    ]

def __get_argument_info(
    name: str,
    object_type: Type[Any],
    default_value: Any,
    default_factory: Any) -> ArgumentInfo:
    if (origin := getattr(object_type, "__origin__", None)) is None:
        return ArgumentInfo(name, object_type, None, False, default_value, default_factory)

    allows_none = False
    if origin == Union:
        allows_none = True
        object_type = get_args(object_type)[0]
        origin = getattr(object_type, "__origin__", None)

    if origin is None:
        return ArgumentInfo(name, object_type, None, allows_none, default_value, default_factory)

    if origin == tuple:
        args = get_args(object_type)
        if len(args) != 2 or args[-1] != Ellipsis:
            raise ValueError("Expected a tuple with two arguments, the second being an ellipsis.")
        return ArgumentInfo(name, args[0], tuple, allows_none, default_value, default_factory)

    if origin == list:
        args = get_args(object_type)
        return ArgumentInfo(name, args[0], list, allows_none, default_value, default_factory)

    raise ValueError(f"Expected a tuple or a list, but got '{object_type}'.")
