from ..exceptions import ArgumentError
from typing import TypeVar

T = TypeVar("T")

def assert_not_none(obj: T, argument_name: str) -> T:
    if obj is None:
        raise ArgumentError(argument_name, f"The argument must have a value.")
    return obj
