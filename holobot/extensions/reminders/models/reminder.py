from ..enums import DayOfWeek
from datetime import date, datetime, timedelta
from typing import Optional

class Reminder:
    def __init__(self) -> None:
        self.id = 0
        self.user_id = ""
        self.message = ""
        self.created_at = datetime.utcnow()
        self.is_repeating = False
        self.frequency_time = timedelta()
        self.day_of_week = DayOfWeek.SUNDAY
        self.until_date = None
        self.last_trigger = datetime.utcnow()
        self.next_trigger = datetime.utcnow()

    @property
    def id(self) -> int:
        return self.__id
        
    @id.setter
    def id(self, value: int) -> None:
        self.__id = value
    
    @property
    def user_id(self) -> str:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        self.__user_id = value
    
    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        self.__message = value
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self.__created_at = value
    
    @property
    def is_repeating(self) -> bool:
        return self.__is_repeating

    @is_repeating.setter
    def is_repeating(self, value: bool) -> None:
        self.__is_repeating = value
    
    @property
    def frequency_time(self) -> timedelta:
        return self.__frequency_time

    @frequency_time.setter
    def frequency_time(self, value: timedelta) -> None:
        self.__frequency_time = value
    
    @property
    def day_of_week(self) -> DayOfWeek:
        return self.__day_of_week

    @day_of_week.setter
    def day_of_week(self, value: DayOfWeek) -> None:
        self.__day_of_week = value
    
    @property
    def until_date(self) -> Optional[date]:
        return self.__until_date

    @until_date.setter
    def until_date(self, value: Optional[date]) -> None:
        self.__until_date = value
    
    @property
    def last_trigger(self) -> datetime:
        return self.__last_trigger

    @last_trigger.setter
    def last_trigger(self, value: datetime) -> None:
        self.__last_trigger = value
    
    @property
    def next_trigger(self) -> datetime:
        return self.__next_trigger

    @next_trigger.setter
    def next_trigger(self, value: datetime) -> None:
        self.__next_trigger = value
    
    @property
    def is_expired(self) -> bool:
        if self.until_date is None:
            return False
        return self.__next_trigger.date() > self.until_date
    
    def __str__(self) -> str:
        return (
            "<Reminder id: {}, repeats: {}, last trigger: {}, next trigger: {}, frequency: {}>"
        ).format(self.id, self.is_repeating, self.last_trigger, self.next_trigger, self.frequency_time)

    def recalculate_next_trigger(self) -> None:
        if not self.is_repeating:
            raise ValueError("A non-recurring reminder cannot have a new trigger date-time.")
        current_time = datetime.utcnow()
        trigger_time = self.last_trigger + self.frequency_time
        self.next_trigger = trigger_time if trigger_time > current_time else current_time
