from collections.abc import Awaitable, Callable
from queue import Queue
from typing import Any, TypeVar

from holobot.sdk.utils.type_utils import UNDEFINED, UndefinedType

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
    if isinstance(value := dictionary.get(key, UNDEFINED), UndefinedType):
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
    if isinstance(value := dictionary.get(key, UNDEFINED), UndefinedType):
        value = await add_factory(key)
    else:
        value = await update_factory(key, value)

    dictionary[key] = value
    return value

def merge(
    target: dict[str, Any],
    source: dict[str, Any],
    mutate_target: bool = True
) -> dict[str, Any]:
    """Merges the source dictionary's contents onto the target dictionary's contents.

    If mutation is disabled, a new dictionary is created.

    :param target: The base dictionary.
    :type target: dict[str, Any]
    :param source: The dictionary with the new contents.
    :type source: dict[str, Any]
    :param mutate_target: Whether to merge the source into the target or create a new dictionary, defaults to True
    :type mutate_target: bool, optional
    :return: A new dictionary with the merged contents.
    :rtype: dict[str, Any]
    """

    pairs = Queue[tuple[dict[str, Any], dict[str, Any]]]()
    result = target if mutate_target else dict(target)
    pairs.put((result, source))
    while not pairs.empty():
        t, s = pairs.get()
        for key in s:
            if not key in t or not isinstance(s[key], dict):
                t[key] = s[key]
                continue

            pairs.put((t[key], s[key]))

    return result

def get_generic(
    source: dict[TKey, Any],
    value_type: type[TValue],
    key: TKey
) -> TValue | UndefinedType:
    if key not in source:
        return UNDEFINED

    value = source[key]
    if not isinstance(value, value_type):
        return UNDEFINED

    return value
