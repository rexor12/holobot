from typing import Callable, Generator, Iterable, TypeVar

T = TypeVar("T")

def where(iterable: Iterable[T], predicate: Callable[[T], bool]) -> Generator[T, None, None]:
    if iterable is None:
        raise ValueError("The iterable must be specified.")
    if predicate is None:
        raise ValueError("The predicate must be specified.")
    for item in iterable:
        if predicate(item):
            yield item

def has_any(iterable: Iterable[T], predicate: Callable[[T], bool]) -> bool:
    return first_or_default(iterable, predicate) is not None

def first_or_default(iterable: Iterable[T], predicate: Callable[[T], bool] | None = None, default_value: T | None = None) -> T | None:
    if predicate is None:
        return next(iter(iterable), default_value)
    return next(where(iterable, predicate), default_value)
