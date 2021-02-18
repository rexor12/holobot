from typing import Callable, Coroutine, Dict, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

def get_or_add(dictionary: Dict[TKey, TValue], key: TKey, value: TValue) -> TValue:
    existing_value = dictionary.get(key, None)
    if not existing_value:
        dictionary[key] = existing_value = value
    return existing_value
