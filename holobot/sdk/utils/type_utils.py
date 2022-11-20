from typing import Any, Literal, TypeVar

class Singleton(type):
    __instance: Any | None = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance

class UndefinedType(metaclass=Singleton):
    __slots__ = ()

    def __bool__(self) -> Literal[False]:
        return False

UNDEFINED: UndefinedType = UndefinedType()

T = TypeVar("T", covariant=True)

UndefinedOr = UndefinedType | T
"""Alias for a type that is either UndefinedType or the specified type."""

UndefinedOrNoneOr = UndefinedOr[T] | None
"""Alias for a type that is either UndefinedType, None or the specified type."""

def get_fully_qualified_name(clazz: type):
    module_name = clazz.__module__
    class_name = clazz.__qualname__
    # To avoid outputting "__builtin__", we check for the always available
    # str type's module, which is known to be exactly that.
    if module_name in (None, str.__class__.__module__):
        return class_name
    return ".".join((module_name, class_name))
