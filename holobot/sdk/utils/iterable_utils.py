from .exception_utils import assert_range
from typing import Callable, Generator, Iterable, Optional, TypeVar

import sys

T = TypeVar("T")

def first_or_default(iterable: Iterable[T], predicate: Optional[Callable[[T], bool]] = None, default_value: Optional[T] = None) -> Optional[T]:
    if predicate is None:
        return next(iter(iterable), default_value)
    return next(where(iterable, predicate), default_value)

def has_any(iterable: Iterable[T], predicate: Callable[[T], bool]) -> bool:
    return first_or_default(iterable, predicate) is not None

def take(iterable: Iterable[T], count: int) -> Generator[T, None, None]:
    assert_range(count, 0, sys.maxsize, "count")
    if count == 0:
        return

    taken = 0
    for item in iterable:
        yield item
        taken += 1
        if taken == count:
            break

def where(iterable: Iterable[T], predicate: Callable[[T], bool]) -> Generator[T, None, None]:
    if iterable is None:
        raise ValueError("The iterable must be specified.")
    if predicate is None:
        raise ValueError("The predicate must be specified.")
    for item in iterable:
        if predicate(item):
            yield item
