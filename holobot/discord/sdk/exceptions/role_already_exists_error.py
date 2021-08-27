class RoleAlreadyExistsError(Exception):
    def __init__(self, role_name: str, *args: object) -> None:
        super().__init__(*args)
        self.__role_name: str = role_name
    
    @property
    def role_name(self) -> str:
        return self.__role_name
