from typing import TypeVar

T = TypeVar("T")

def pad_left(list: list[T], value: T, length: int) -> list[T]:
    if length < 0:
        raise ValueError("Length cannot be less than zero.")
    if length < len(list):
        length = len(list)
    padded_list = [value for _ in range(0, length)]
    original_length = len(list)
    for index in range(0, len(list)):
        padded_list[length - index - 1] = list[original_length - index - 1]
    return padded_list
