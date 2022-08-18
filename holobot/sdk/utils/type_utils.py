from typing import Any, Type

class Singleton(type):
    __instance: Type | None = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance

class _UndefinedType(metaclass=Singleton):
    __slots__ = ()
    __bool__ = lambda self: False

UNDEFINED = _UndefinedType()

def get_fully_qualified_name(clazz: Type[Any]):
    module_name = clazz.__module__
    class_name = clazz.__qualname__
    # To avoid outputting "__builtin__", we check for the always available
    # str type's module, which is known to be exactly that.
    if module_name in (None, str.__class__.__module__):
        return class_name
    return ".".join((module_name, class_name))
