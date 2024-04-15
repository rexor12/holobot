from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def pad_left(source: list[T], value: T, length: int) -> list[T]:
    if length < 0:
        raise ValueError("Length cannot be less than zero.")
    length = max(length, len(source))
    return [value] * (length - len(source)) + source

def binary_search_lower(
    source: list[T],
    selector: Callable[[T], int],
    value: int
) -> int:
    """Finds the value equal to or lower than the specified value in an ordered list.

    :param source: The ordered list.
    :type source: list[T]
    :param selector: A projection of the items in the list to search.
    :type selector: Callable[[T], int]
    :param value: The value to find.
    :type value: int
    :return: The index of the matching value, or -1 if the list is empty.
    :rtype: int
    """

    if not source:
        return -1

    left, right = 0, len(source) - 1
    satisfying_index = 0
    while left <= right:
        mid = left + (right - left) // 2
        if selector(source[mid]) <= value:
            satisfying_index = mid
            left = mid + 1
        else:
            right = mid - 1

    return satisfying_index
