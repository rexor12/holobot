from .database_error import DatabaseError

class SerializationError(DatabaseError):
    def __init__(self, *args) -> None:
        super().__init__(*args)
