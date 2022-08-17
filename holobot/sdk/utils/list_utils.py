from typing import TypeVar

T = TypeVar("T")

def pad_left(list_: list[T], value: T, length: int) -> list[T]:
    if length < 0:
        raise ValueError("Length cannot be less than zero.")
    length = max(length, len(list_))
    return [value] * (length - len(list_)) + list_
