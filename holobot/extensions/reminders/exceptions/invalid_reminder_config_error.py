class InvalidReminderConfigError(Exception):
    def __init__(self, param1: str, param2: str, *args) -> None:
        super().__init__(*args)
        self.param1 = param1
        self.param2 = param2
    
    @property
    def param1(self) -> str:
        return self.__param1
    
    @param1.setter
    def param1(self, value: str) -> None:
        self.__param1 = value
    
    @property
    def param2(self) -> str:
        return self.__param2
    
    @param2.setter
    def param2(self, value: str) -> None:
        self.__param2 = value
