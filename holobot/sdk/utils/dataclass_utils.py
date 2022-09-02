import builtins
import types
import typing
from collections.abc import Sequence
from dataclasses import _MISSING_TYPE, fields, is_dataclass

from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.utils import first

class ArgumentInfo(typing.NamedTuple):
    name: str
    object_type: type
    collection_constructor: type | None
    allows_none: bool
    default_value: typing.Any
    default_factory: typing.Callable[[], typing.Any] | None

def get_argument_infos(dataclass_type: type) -> Sequence[ArgumentInfo]:
    if not is_dataclass(dataclass_type):
        raise ArgumentError("dataclass_type", "The type must be a dataclass.")

    initializer = getattr(dataclass_type, "__init__", None)
    if not initializer:
        raise ValueError(f"Type '{dataclass_type}' has no __init__ method.")

    # Need to explicitly load type hints for dataclasses.
    # See: https://stackoverflow.com/a/55938344
    resolved_type_hints = typing.get_type_hints(initializer)

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
    default_value: typing.Any,
    default_factory: typing.Any
) -> ArgumentInfo:
    match origin := typing.get_origin(object_type):
        case None:
            return ArgumentInfo(name, object_type, None, False, default_value, default_factory)
        case typing.Union | types.UnionType:
            args = typing.get_args(object_type)
            if len(args) != 2 or None not in args:
                raise ValueError(f"Expected a Union with two arguments, the second being None, but got {args!r} instead.")
            object_type = first(typing.cast(tuple[type, ...], args), lambda i: i and i is not None)
            origin = typing.get_origin(object_type)

    match origin:
        case None:
            return ArgumentInfo(name, object_type, None, True, default_value, default_factory)
        case builtins.tuple | builtins.list:  # Needs dot notation: https://peps.python.org/pep-0634/#value-patterns
            args = typing.get_args(object_type)
            if origin is tuple and (len(args) != 2 or args[1] is not Ellipsis):
                raise ValueError(f"Expected a tuple with two arguments, the second being Ellipsis, but got {args!r} instead.")
            return ArgumentInfo(name, args[0], origin, True, default_value, default_factory)
        case _:
            raise ValueError(f"Expected None, tuple or list type, but got '{object_type}'.")
