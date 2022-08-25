from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")

def has_any(iterable: Iterable[T], predicate: Callable[[T], bool]) -> bool:
    return first_or_default(iterable, predicate) is not None

def first(iterable: Iterable[T], predicate: Callable[[T], bool] | None = None) -> T:
    return (
        next(iter(iterable))
        if predicate is None
        else next(filter(predicate, iterable))
    )

def first_or_default(
    iterable: Iterable[T],
    predicate: Callable[[T], bool] | None = None,
    default_value: T | None = None
) -> T | None:
    return (
        next(iter(iterable), default_value)
        if predicate is None
        else next(filter(predicate, iterable), default_value)
    )
