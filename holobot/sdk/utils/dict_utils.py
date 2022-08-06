from typing import Callable, Dict, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")
TState = TypeVar("TState")

def get_or_add(
    dictionary: Dict[TKey, TValue],
    key: TKey,
    value_factory: Callable[[TState], TValue],
    state: TState
) -> TValue:
    existing_value = dictionary.get(key, None)
    if not existing_value:
        dictionary[key] = existing_value = value_factory(state)
    return existing_value
