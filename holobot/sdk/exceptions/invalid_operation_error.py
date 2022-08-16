class InvalidOperationError(Exception):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "The object is in a state that doesn't allow the operation to be performed.")
