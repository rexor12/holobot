from datetime import datetime

class WarnStrike:
    def __init__(self) -> None:
        self.id = -1
        self.created_at = datetime.utcnow()
        self.server_id = ""
        self.user_id = ""
        self.reason = ""
        self.warner_id = ""

    @property
    def id(self) -> int:
        return self.__id
    
    @id.setter
    def id(self, value: int) -> None:
        self.__id = value

    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self.__created_at = value

    @property
    def server_id(self) -> str:
        return self.__server_id
    
    @server_id.setter
    def server_id(self, value: str) -> None:
        self.__server_id = value

    @property
    def user_id(self) -> str:
        return self.__user_id
    
    @user_id.setter
    def user_id(self, value: str) -> None:
        self.__user_id = value

    @property
    def reason(self) -> str:
        return self.__reason
    
    @reason.setter
    def reason(self, value: str) -> None:
        self.__reason = value

    @property
    def warner_id(self) -> str:
        return self.__warner_id
    
    @warner_id.setter
    def warner_id(self, value: str) -> None:
        self.__warner_id = value
