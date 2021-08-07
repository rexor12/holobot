class ArgumentError(Exception):
    def __init__(self, argument_name: str, *args) -> None:
        super().__init__(*args)
        self.argument_name = argument_name
    
    @property
    def argument_name(self) -> str:
        return self.__argument_name

    @argument_name.setter
    def argument_name(self, value: str) -> None:
        self.__argument_name = value
    
    def __str__(self) -> str:
        return f"{super().__str__()}\nArgument name: {self.argument_name}"
