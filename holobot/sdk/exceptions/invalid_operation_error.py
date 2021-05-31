from typing import Optional

class InvalidOperationError(Exception):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The object is in a state that doesn't allow the operation to be performed.")
