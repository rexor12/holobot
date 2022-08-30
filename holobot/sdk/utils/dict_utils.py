from collections.abc import Awaitable, Callable
from typing import TypeVar

from holobot.sdk.utils.type_utils import UNDEFINED

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

def add_or_update(
    dictionary: dict[TKey, TValue],
    key: TKey,
    add_factory: Callable[[TKey], TValue],
    update_factory: Callable[[TKey, TValue], TValue]
) -> TValue:
    if (value := dictionary.get(key, UNDEFINED)) is UNDEFINED:
        value = add_factory(key)
    else:
        value = update_factory(key, value)

    dictionary[key] = value
    return value

async def add_or_update_async(
    dictionary: dict[TKey, TValue],
    key: TKey,
    add_factory: Callable[[TKey], Awaitable[TValue]],
    update_factory: Callable[[TKey, TValue], Awaitable[TValue]]
) -> TValue:
    if (value := dictionary.get(key, UNDEFINED)) is UNDEFINED:
        value = await add_factory(key)
    else:
        value = await update_factory(key, value)

    dictionary[key] = value
    return value
