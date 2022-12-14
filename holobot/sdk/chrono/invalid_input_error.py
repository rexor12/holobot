class InvalidInputError(Exception):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message)
