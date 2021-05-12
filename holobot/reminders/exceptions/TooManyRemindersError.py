class TooManyRemindersError(Exception):
    def __init__(self, reminder_count: int, *args) -> None:
        super().__init__(*args)
        self.reminder_count = reminder_count
    
    @property
    def reminder_count(self) -> int:
        return self.__reminder_count

    @reminder_count.setter
    def reminder_count(self, value: int) -> None:
        self.__reminder_count = value