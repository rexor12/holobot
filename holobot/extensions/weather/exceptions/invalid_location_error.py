class InvalidLocationError(Exception):
    def __init__(self, requested_location: str, *args):
        super().__init__(*args)
        self.__requested_location: str = requested_location
    
    @property
    def requested_location(self) -> str:
        return self.__requested_location
