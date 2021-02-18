class AuthorizationError(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"Unauthorized access from the user with the identifier '{user_id}'.")