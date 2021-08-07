class QueryFailedError(Exception):
    def __init__(self, query: str, *args: object) -> None:
        super().__init__(*args)
        self.__query: str = query
    
    @property
    def query(self) -> str:
        return self.__query
