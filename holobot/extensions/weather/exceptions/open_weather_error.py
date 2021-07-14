class OpenWeatherError(Exception):
    def __init__(self, error_code: str, requested_location: str, *args):
        super().__init__(*args)
        self.__error_code: str = error_code
        self.__requested_location: str = requested_location
    
    @property
    def error_code(self) -> str:
        return self.__error_code
    
    @property
    def requested_location(self) -> str:
        return self.__requested_location
