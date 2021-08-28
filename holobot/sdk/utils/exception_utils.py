from ..exceptions import ArgumentError, ArgumentOutOfRangeError
from ..math import ComparableProtocol
from typing import TypeVar

T = TypeVar("T")
TComparable = TypeVar("TComparable", bound=ComparableProtocol)

def assert_not_none(obj: T, argument_name: str) -> T:
    if obj is None:
        raise ArgumentError(argument_name, f"The argument must have a value.")

    return obj

def assert_range(
    obj: TComparable,
    lower_bound: TComparable,
    upper_bound: TComparable,
    argument_name: str) -> TComparable:
    if obj < lower_bound or obj > upper_bound:
        raise ArgumentOutOfRangeError(argument_name, str(lower_bound), str(upper_bound))

    return obj
