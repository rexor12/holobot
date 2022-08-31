import traceback
from typing import TypeVar

from ..exceptions import ArgumentError, ArgumentOutOfRangeError
from ..math import ComparableProtocol

T = TypeVar("T")
TComparable = TypeVar("TComparable", ComparableProtocol, int, float)

def assert_not_none(obj: T, argument_name: str) -> T:
    if obj is None:
        raise ArgumentError(argument_name, "The argument must have a value.")

    return obj

def assert_range(
    obj: TComparable,
    lower_bound: TComparable,
    upper_bound: TComparable,
    argument_name: str
) -> TComparable:
    if obj < lower_bound or obj > upper_bound:
        raise ArgumentOutOfRangeError(argument_name, str(lower_bound), str(upper_bound))

    return obj

def format_exception(exception: Exception) -> str:
    """Pretty-print an exception.

    :param exception: The exception to be formatted.
    :type exception: Exception
    :return: A formatted description of the exception.
    :rtype: str
    """

    formatted_string = "".join(traceback.format_exception(exception))
    return formatted_string.rstrip()
