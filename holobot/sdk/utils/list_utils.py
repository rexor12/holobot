from typing import TypeVar

T = TypeVar("T")

def pad_left(source: list[T], value: T, length: int) -> list[T]:
    if length < 0:
        raise ValueError("Length cannot be less than zero.")
    length = max(length, len(source))
    return [value] * (length - len(source)) + source
