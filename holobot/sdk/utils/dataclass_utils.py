from collections.abc import Sequence
from dataclasses import _MISSING_TYPE, fields, is_dataclass
from types import NoneType, UnionType
from typing import Any, Callable, NamedTuple, Union, cast, get_args, get_type_hints

from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.utils import first

class ArgumentInfo(NamedTuple):
    name: str
    object_type: type
    collection_constructor: type | None
    allows_none: bool
    default_value: Any
    default_factory: Callable[[], Any] | None

def get_argument_infos(dataclass_type: type) -> Sequence[ArgumentInfo]:
    if not is_dataclass(dataclass_type):
        raise ArgumentError("dataclass_type", "The type must be a dataclass.")

    initializer = getattr(dataclass_type, "__init__", None)
    if not initializer:
        raise ValueError(f"Type '{dataclass_type}' has no __init__ method.")

    # Need to explicitly load type hints for dataclasses.
    # See: https://stackoverflow.com/a/55938344
    resolved_type_hints = get_type_hints(initializer)

    return [
        __get_argument_info(
            field_info.name,
            resolved_type_hints[field_info.name],
            None if isinstance(field_info.default, _MISSING_TYPE) else field_info.default,
            None if isinstance(field_info.default_factory, _MISSING_TYPE) else field_info.default_factory
        ) for field_info in fields(dataclass_type)
    ]

def __get_argument_info(
    name: str,
    object_type: type,
    default_value: Any,
    default_factory: Any
) -> ArgumentInfo:
    if isinstance(object_type, UnionType):
        origin = UnionType
    elif (origin := getattr(object_type, "__origin__", None)) is None:
        return ArgumentInfo(name, object_type, None, False, default_value, default_factory)

    allows_none = False
    if origin in (Union, UnionType):
        args = get_args(object_type)
        if len(args) != 2 or NoneType not in args:
            raise ValueError((
                "Expected an optional type (NoneType or other),"
                f" but '{name}' in '{object_type}' is diferent ({args})."
            ))

        allows_none = True
        object_type = first(cast(tuple[type, ...], args), lambda i: i and i is not NoneType)
        origin = getattr(object_type, "__origin__", None)

    if origin is None:
        return ArgumentInfo(name, object_type, None, allows_none, default_value, default_factory)

    if origin == tuple:
        args = get_args(object_type)
        if len(args) != 2 or args[-1] != Ellipsis:
            raise ValueError((
                "Expected a tuple with two arguments, the second being an ellipsis,"
                f" but got {args} instead."
            ))
        return ArgumentInfo(name, args[0], tuple, allows_none, default_value, default_factory)

    if origin == list:
        args = get_args(object_type)
        return ArgumentInfo(name, args[0], list, allows_none, default_value, default_factory)

    raise ValueError(f"Expected a tuple or an optional, tuple or list type, but got '{object_type}'.")
