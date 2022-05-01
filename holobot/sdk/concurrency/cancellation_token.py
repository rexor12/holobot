class CancellationToken:
    def __init__(self, is_cancelled: bool = False) -> None:
        self.__is_cancellation_requested: bool = is_cancelled
    
    @property
    def is_cancellation_requested(self) -> bool:
        return self.__is_cancellation_requested
    
    def cancel(self) -> None:
        self.__is_cancellation_requested = True

EMPTY_CANCELLATION_TOKEN = CancellationToken(False)
