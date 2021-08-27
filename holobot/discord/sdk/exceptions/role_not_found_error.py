class RoleNotFoundError(Exception):
    def __init__(self, role_id: str, *args: object) -> None:
        super().__init__(*args)
        self.__role_id: str = role_id
    
    @property
    def role_id(self) -> str:
        return self.__role_id
