class ArgumentOutOfRangeError(Exception):
    def __init__(self, argument_name: str, lower_bound: str, upper_bound: str, *args):
        super().__init__(*args)
        self.argument_name = argument_name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
    
    @property
    def argument_name(self) -> str:
        return self.__argument_name

    @argument_name.setter
    def argument_name(self, value: str) -> None:
        self.__argument_name = value
    
    @property
    def lower_bound(self) -> str:
        return self.__lower_bound

    @lower_bound.setter
    def lower_bound(self, value: str) -> None:
        self.__lower_bound = value
    
    @property
    def upper_bound(self) -> str:
        return self.__upper_bound

    @upper_bound.setter
    def upper_bound(self, value: str) -> None:
        self.__upper_bound = value
