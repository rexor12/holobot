class OpenWeatherError(Exception):
    @property
    def error_code(self) -> str:
        return self.__error_code

    @error_code.setter
    def error_code(self, value: str) -> None:
        self.__error_code = value

    @property
    def requested_location(self) -> str:
        return self.__requested_location

    @requested_location.setter
    def requested_location(self, value: str) -> None:
        self.__requested_location = value

    def __init__(self, error_code: str, requested_location: str, *args):
        super().__init__(*args)
        self.error_code = error_code
        self.requested_location = requested_location

    def __str__(self) -> str:
        return f"{super().__str__()}\nError code: {self.error_code}, location: {self.requested_location}"
