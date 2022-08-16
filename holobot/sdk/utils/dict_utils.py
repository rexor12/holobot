from typing import Callable, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")
TState = TypeVar("TState")

def get_or_add(
    dictionary: dict[TKey, TValue],
    key: TKey,
    value_factory: Callable[[TState], TValue],
    state: TState
) -> TValue:
    if key in dictionary:
        return dictionary[key]
    dictionary[key] = value_factory(state)
    return dictionary[key]
