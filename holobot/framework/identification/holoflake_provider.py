import threading
import time

from holobot.sdk.chrono import IClock
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.identification import IHoloflakeProvider, timestamp_to_holo_epoch_offset
from holobot.sdk.identification.holoflake import Holoflake
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment

_MAX_SEQUENCE_ID: int = (1 << 12) - 1
_SLEEP_TIME: float = 0.0001 # 100 microseconds

@injectable(IHoloflakeProvider)
class HoloflakeProvider(IHoloflakeProvider):
    def __init__(
        self,
        clock: IClock,
        environment: IEnvironment
    ) -> None:
        super().__init__()
        self.__clock = clock
        self.__shard_id = environment.shard_id
        self.__last_timestamp = -1
        self.__sequence = 0
        self.__lock = threading.Lock()

    def get_next_id(self) -> Holoflake:
        with self.__lock:
            current_timestamp = self.__get_current_timestamp()
            if current_timestamp < self.__last_timestamp:
                raise InvalidOperationError(
                    "Holoflakes cannot be generated, because the clock has moved backwards."
                )

            if current_timestamp == self.__last_timestamp:
                self.__sequence += 1
                if self.__sequence > _MAX_SEQUENCE_ID:
                    current_timestamp = self.__wait_for_next_millisecond(current_timestamp)
                    self.__sequence = 0
            else:
                self.__sequence = 0

            self.__last_timestamp = current_timestamp

            return Holoflake.from_segments2(
                current_timestamp,
                self.__shard_id,
                self.__sequence
            )

    def __get_current_timestamp(self) -> int:
        return timestamp_to_holo_epoch_offset(self.__clock.time_utc())

    def __wait_for_next_millisecond(self, current_timestamp: int) -> int:
        while current_timestamp == self.__get_current_timestamp():
            time.sleep(_SLEEP_TIME)

        return self.__get_current_timestamp()
