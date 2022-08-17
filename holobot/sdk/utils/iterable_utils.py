from collections.abc import Callable, Generator, Iterable
from typing import TypeVar

T = TypeVar("T")

def has_any(iterable: Iterable[T], predicate: Callable[[T], bool]) -> bool:
    return first_or_default(iterable, predicate) is not None

def first_or_default(iterable: Iterable[T], predicate: Callable[[T], bool] | None = None, default_value: T | None = None) -> T | None:
    if predicate is None:
        return next(iter(iterable), default_value)
    return next(filter(predicate, iterable), default_value)
