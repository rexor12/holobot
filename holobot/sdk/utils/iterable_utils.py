from collections.abc import Callable, Generator, Iterable, Sequence
from typing import Any, TypeVar

from holobot.sdk.exceptions import ArgumentError

T = TypeVar("T")
T2 = TypeVar("T2")

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

def find_or_none(
    iterable: Iterable[T],
    predicate: Callable[[T], bool]
) -> int | None:
    for index, item in enumerate(iterable):
        if predicate(item):
            return index

    return None

def select_many(
    iterable: Iterable[T],
    transformer: Callable[[T], Iterable[T2]]
) -> Iterable[T2]:
    for item in iterable:
        for subitem in transformer(item):
            yield subitem

def multi_to_dict(
    iterable: Iterable[T],
    key_selector: Callable[[T], Iterable[T2]]
) -> dict[T2, T]:
    result = dict[T2, T]()
    for item in iterable:
        for key in key_selector(item):
            if key in result:
                raise ArgumentError("iterable", f"Duplicate key '{str(key)}'.")

            result[key] = item

    return result

def group_by_types(
    iterable: Iterable[T],
    grouping_types: tuple[type, ...]
) -> dict[type, Sequence[T]]:
    result = dict[type, Sequence[T]]()
    for grouping_type in grouping_types:
        group = list[T]()
        for item in iterable:
            if isinstance(item, grouping_type):
                group.append(item)

        result[grouping_type] = group

    return result

def concat(
    iterable1: Iterable[T],
    iterable2: Iterable[T]
) -> Generator[T, Any, None]:
    for item in iterable1:
        yield item

    for item in iterable2:
        yield item

def of_type(
    iterable: Iterable[T],
    item_type: type[T2]
) -> Generator[T2, Any, None]:
    for item in iterable:
        if isinstance(item, item_type):
            yield item

def batch(
    iterable: Iterable[T],
    batch_size: int
) -> Generator[Iterable[T], Any, None]:
    iterator = iterable.__iter__()
    items: list[T] = []
    has_items = True
    while has_items:
        try:
            for _ in range(batch_size):
                items.append(iterator.__next__())
        except StopIteration:
            has_items = False

        if len(items) > 0:
            yield items

        items.clear()
