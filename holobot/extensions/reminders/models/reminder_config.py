from datetime import timedelta

class ReminderConfig:
    def __init__(self) -> None:
        self.in_time = self.at_time = self.every_interval = None
        self.message = ""

    @property
    def in_time(self) -> timedelta | None:
        return self.__in_time

    @in_time.setter
    def in_time(self, value: timedelta | None) -> None:
        self.__in_time = value

    @property
    def at_time(self) -> timedelta | None:
        return self.__at_time

    @at_time.setter
    def at_time(self, value: timedelta | None) -> None:
        self.__at_time = value

    @property
    def every_interval(self) -> timedelta | None:
        return self.__every_interval

    @every_interval.setter
    def every_interval(self, value: timedelta | None) -> None:
        self.__every_interval = value

    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        self.__message = value
