from datetime import timedelta
from typing import Optional

class ReminderConfig:
    def __init__(self) -> None:
        self.in_time = self.at_time = self.every_interval = None
        self.message = ""

    @property
    def in_time(self) -> Optional[timedelta]:
        return self.__in_time
    
    @in_time.setter
    def in_time(self, value: Optional[timedelta]) -> None:
        self.__in_time = value

    @property
    def at_time(self) -> Optional[timedelta]:
        return self.__at_time
    
    @at_time.setter
    def at_time(self, value: Optional[timedelta]) -> None:
        self.__at_time = value

    @property
    def every_interval(self) -> Optional[timedelta]:
        return self.__every_interval
    
    @every_interval.setter
    def every_interval(self, value: Optional[timedelta]) -> None:
        self.__every_interval = value

    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        self.__message = value
