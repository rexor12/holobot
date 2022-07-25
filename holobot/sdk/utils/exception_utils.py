from io import StringIO
from typing import TypeVar

import traceback

from ..exceptions import ArgumentError, ArgumentOutOfRangeError
from ..math import ComparableProtocol

T = TypeVar("T")
TComparable = TypeVar("TComparable", ComparableProtocol, int, float)

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

def format_exception(exception: Exception) -> str:
    """Pretty-print an exception.

    Shamelessly stolen from structlog.

    :param exception: The exception to be formatted.
    :type exception: Exception
    :return: A formatted description of the exception.
    :rtype: str
    """

    string_buffer = StringIO()
    traceback.print_exception(exception, limit=None, file=string_buffer)
    formatted_string = string_buffer.getvalue()
    string_buffer.close()
    if formatted_string[-1:] == "\n":
        formatted_string = formatted_string[:-1]

    return formatted_string
