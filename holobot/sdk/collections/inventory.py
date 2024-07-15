from collections.abc import Iterator, Sequence
from typing import Generic, SupportsIndex, TypeVar

TItem = TypeVar("TItem")

class Inventory(Generic[TItem]):
    @property
    def slot_count(self) -> int:
        return self.__slot_count

    @property
    def slots(self) -> Sequence[TItem | None]:
        return self.__slots

    def __init__(
        self,
        slot_count: int
    ) -> None:
        super().__init__()
        self.__slot_count = slot_count
        self.__slots: list[TItem | None] = [None] * slot_count

    def get_item(self, slot_index: int) -> TItem | None:
        return self[slot_index]

    def set_item(self, slot_index: int, item: TItem) -> None:
        self[slot_index] = item

    def remove_item(self, slot_index: int) -> TItem | None:
        item = self.__slots[slot_index]
        self.__slots[slot_index] = None

        return item

    def __getitem__(self, i: SupportsIndex, /) -> TItem | None:
        return self.__slots[i]

    def __setitem__(self, key: SupportsIndex, value: TItem | None, /) -> None:
        self.__slots[key] = value

    def __iter__(self) -> Iterator[TItem | None]:
        return self.__slots.__iter__()
