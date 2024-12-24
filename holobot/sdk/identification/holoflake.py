from __future__ import annotations

import typing
from collections.abc import Sequence
from datetime import datetime

from .holoflake_utils import (
    datetime_to_holo_epoch_offset, holo_epoch_offset_to_datetime, timestamp_to_holo_epoch_offset
)

@typing.final
class Holoflake(int):
    """Holo's implementation of Twitter's Snowflake."""

    __slots__: Sequence[str] = ()

    @property
    def created_at(self) -> datetime:
        epoch_offset = self >> 22
        return holo_epoch_offset_to_datetime(epoch_offset)

    @property
    def worker_id(self) -> int:
        return (self & 0x3F_F000) >> 12

    @property
    def sequence_id(self) -> int:
        return self & 0xFFF

    @staticmethod
    def from_segments(timestamp: datetime, worker_id: int, sequence_id: int) -> Holoflake:
        return Holoflake(
            (datetime_to_holo_epoch_offset(timestamp) << 22)
            | (worker_id << 12)
            | sequence_id
        )

    @staticmethod
    def from_segments2(timestamp: int, worker_id: int, sequence_id: int) -> Holoflake:
        return Holoflake((timestamp << 22) | (worker_id << 12) | sequence_id)

    @staticmethod
    def min() -> Holoflake:
        return Holoflake(0)

    @staticmethod
    def max() -> Holoflake:
        return Holoflake((1 << 63) - 1)
