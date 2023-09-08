from typing import Any

class HttpStatusError(Exception):
    @property
    def status_code(self) -> int:
        return self.__status_code

    @status_code.setter
    def status_code(self, value: int) -> None:
        self.__status_code = value

    @property
    def attrs(self) -> dict[str, Any]:
        return self.__attrs

    @attrs.setter
    def attrs(self, value: dict[str, Any]) -> None:
        self.__attrs = value

    def __init__(self, status_code: int, message: str | None = None, **attrs) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.attrs = attrs

    def __str__(self) -> str:
        return f"{super().__str__()}\nStatus code: {self.status_code}"
