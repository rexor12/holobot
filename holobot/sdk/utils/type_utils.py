from typing import Any, Type

def get_fully_qualified_name(clazz: Type[Any]):
    module_name = clazz.__module__
    class_name = clazz.__qualname__
    # To avoid outputting "__builtin__", we check for the always available
    # str type's module, which is known to be exactly that.
    if module_name in (None, str.__class__.__module__):
        return class_name
    return ".".join((module_name, class_name))
